# HMI/pages/monitor.py
import datetime
import json  # para JSON por línea
import customtkinter as ctk
from .base import BasePage
from ..theme import BG_MAIN, PANEL, TXT

class MonitorSeriePage(BasePage):
    title = "Monitor Serie"
    subtitle = "Entradas (RX) y salidas (TX) con opciones TS/CRLF"

    # antes: def __init__(..., serial_manager, info_status_cb, **kwargs)
    def __init__(self, master, serial_manager, info_status_cb, dashboard=None, **kwargs):
        super().__init__(master, **kwargs)
        self.serial = serial_manager
        self.info_status = info_status_cb
        self.dashboard = dashboard       # ← MISMA instancia de Dashboard
        self._line_buf = ""              # buffer para armar líneas completas

        # ===== UI básica (ajústala a tu versión si ya la tienes) =====
        opts = ctk.CTkFrame(self, fg_color=BG_MAIN)
        opts.pack(fill="x", padx=12, pady=(4, 0))

        self.ts_var   = ctk.BooleanVar(value=True)
        self.crlf_var = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(opts, text="Timestamp", variable=self.ts_var).pack(side="left", padx=(0, 12))
        ctk.CTkCheckBox(opts, text="CR/LF al enviar", variable=self.crlf_var).pack(side="left")

        # RX / TX
        body = ctk.CTkFrame(self, fg_color=BG_MAIN)
        body.pack(fill="both", expand=True, padx=12, pady=12)
        body.grid_columnconfigure((0, 1), weight=1, uniform="cols")
        body.grid_rowconfigure(0, weight=1)

        rx_box = ctk.CTkFrame(body, fg_color=PANEL)
        tx_box = ctk.CTkFrame(body, fg_color=PANEL)
        rx_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        tx_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.txt_rx = ctk.CTkTextbox(rx_box, wrap="none")
        self.txt_rx.pack(fill="both", expand=True, padx=8, pady=8)

        self.txt_tx = ctk.CTkTextbox(tx_box, height=80, wrap="none")
        self.txt_tx.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkButton(tx_box, text="Enviar", command=self._send).pack(padx=8, pady=(0, 8), anchor="e")

    # ====== Métodos utilitarios ======
    def _append(self, widget: ctk.CTkTextbox, text: str):
        widget.configure(state="normal")
        widget.insert("end", text)
        widget.see("end")
        widget.configure(state="disabled")

    def _send(self):
        data = self.txt_tx.get("1.0", "end").rstrip("\n")
        if not data:
            return
        if self.crlf_var.get():
            data += "\r\n"
        else:
            data += "\n"
        ok = self.serial.write_line(data, crlf=False)  # ya agregamos fin de línea
        if ok:
            self.info_status("TX enviado.")
        else:
            self.info_status("⚠️ No se pudo enviar.")

    # ====== Lectura + parseo + actualización de Dashboard ======
    def poll_rx_and_render(self, stamped: bool):
        text = self.serial.read_available_text()
        if not text:
            return

        # Render en RX (con timestamp opcional)
        if stamped and self.ts_var.get():
            now = datetime.datetime.now().strftime("%H:%M:%S")
            text_to_show = "".join(
                (f"[{now}] " + ln) if ln.strip() else ln
                for ln in text.splitlines(True)
            )
        else:
            text_to_show = text
        self._append(self.txt_rx, text_to_show)

        # Ensamblar líneas completas y parsear JSON por línea
        self._line_buf += text
        lines = self._line_buf.splitlines(keepends=True)
        if lines and not (lines[-1].endswith("\n") or lines[-1].endswith("\r\n")):
            incomplete = lines[-1]
            lines = lines[:-1]
        else:
            incomplete = ""

        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            # Formato esperado: {"T":24.8,"H":55.2,"V":3.71}
            try:
                obj = json.loads(line)
            except Exception:
                continue

            if isinstance(obj, dict) and self.dashboard:
                low = {str(k).lower(): v for k, v in obj.items()}
                t = low.get("t", low.get("temp", low.get("temperatura")))
                h = low.get("h", low.get("hum",  low.get("humedad")))
                v = low.get("v", low.get("volt", low.get("voltaje", low.get("voltage"))))

                # Setters de la MISMA instancia de dashboard
                if h is not None: self.dashboard.set_hum(h)
                if t is not None: self.dashboard.set_temp(t)
                if v is not None: self.dashboard.set_volt(v)

        self._line_buf = incomplete
