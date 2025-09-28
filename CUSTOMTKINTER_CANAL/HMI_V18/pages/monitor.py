# ============================
# hmi/pages/monitor.py
# ============================
import datetime
import customtkinter as ctk
from .base import BasePage
from ..theme import BG_MAIN, PANEL, TXT, ACCENT, ACCENT_H


class MonitorSeriePage(BasePage):
    title = "Monitor Serie"
    subtitle = "Entradas (RX) y salidas (TX) con opciones TS/CRLF"

    def __init__(self, master, serial_manager, info_status_cb, dashboard_ref=None, **kwargs):
        super().__init__(master, **kwargs)
        self.serial = serial_manager
        self.info_status = info_status_cb

        #tomamos la referencia de la gina de la dashboard desde la app
        self.dashboard_ref = dashboard_ref

        # Opciones
        self.ts_var = ctk.BooleanVar(value=True)
        self.crlf_var = ctk.BooleanVar(value=True)

        # Opciones (TS/CRLF)
        opts = ctk.CTkFrame(self, fg_color=BG_MAIN)
        opts.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkCheckBox(opts, text="ACTIVAR TIME STAMP", variable=self.ts_var).pack(side="left")
        ctk.CTkCheckBox(opts, text="ACTIVAR CR/LF AL ENVIAR", variable=self.crlf_var).pack(side="left", padx=10)

        # Consolas
        consoles = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=10)
        consoles.pack(fill="both", expand=True, padx=16, pady=(4, 12))
        consoles.grid_columnconfigure(0, weight=1)
        consoles.grid_columnconfigure(1, weight=1)
        consoles.grid_rowconfigure(1, weight=1)

        # RX
        ctk.CTkLabel(consoles, text="Entradas (RX)", text_color=TXT, font=("", 13, "bold")) \
            .grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        self.txt_rx = ctk.CTkTextbox(consoles, wrap="word", fg_color=BG_MAIN, text_color=TXT,
                                     font=("Consolas", 12), corner_radius=10, border_width=1, border_color=ACCENT)
        self.txt_rx.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.txt_rx.configure(state="disabled")
        ctk.CTkButton(consoles, text="Limpiar RX", width=110, command=self.clear_rx) \
            .grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))

        # TX
        ctk.CTkLabel(consoles, text="Salidas (TX)", text_color=TXT, font=("", 13, "bold")) \
            .grid(row=0, column=1, sticky="w", padx=10, pady=(10, 0))
        self.txt_tx = ctk.CTkTextbox(consoles, wrap="word", fg_color=BG_MAIN, text_color=TXT,
                                     font=("Consolas", 12), corner_radius=10, border_width=1, border_color=ACCENT)
        self.txt_tx.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.txt_tx.configure(state="disabled")
        ctk.CTkButton(consoles, text="Limpiar TX", width=110, command=self.clear_tx) \
            .grid(row=2, column=1, sticky="w", padx=10, pady=(0, 10))

        # Línea de envío
        tx_row = ctk.CTkFrame(self, fg_color=BG_MAIN)
        tx_row.pack(fill="x", padx=16, pady=(0, 16))

        self.entry = ctk.CTkEntry(tx_row, placeholder_text="Escribe un comando…",
                                  fg_color=PANEL, text_color=TXT, border_width=1, border_color=ACCENT,
                                  corner_radius=8, font=("", 13))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.send())

        ctk.CTkButton(tx_row, text="Enviar", width=120, fg_color=ACCENT,
                      hover_color=ACCENT_H, text_color="white", corner_radius=8,
                      command=self.send).pack(side="left")

    # ---------- API ----------
    def poll_rx_and_render(self, stamped: bool):
        text = self.serial.read_available_text()
        if not text:
            return

        #GUARDAMOS EL TEXTO ORIGINAL ANTES DE ESTAMPARLO
        original_text = text

        if stamped and self.ts_var.get():
            now = datetime.datetime.now().strftime("%H:%M:%S")
            text = "".join((f"[{now}] " + ln) if ln.strip() else ln for ln in text.splitlines(True))
        
        self._append(self.txt_rx, text)

        #Enviamos el texto tal y como lo armamos
        self.dashboard_ref.set_sensors_value(original_text)

        

    def send(self):
        data = self.entry.get().strip()
        if not data:
            return
        ok = self.serial.write_line(data, crlf=self.crlf_var.get())
        if ok:
            out = data + "\n"
            if self.ts_var.get():
                now = datetime.datetime.now().strftime("%H:%M:%S")
                out = f"[{now}] {out}"
            self._append(self.txt_tx, out)
            self.entry.delete(0, "end")
            self.info_status("⬆️ Enviado.")
        else:
            self.info_status("⚠️ Conéctate antes de enviar.")

    def clear_rx(self):
        self._clear(self.txt_rx)
        self.info_status("🧹 RX limpio.")

    def clear_tx(self):
        self._clear(self.txt_tx)
        self.info_status("🧹 TX limpio.")

    # ---------- Helpers ----------
    def _append(self, textbox: ctk.CTkTextbox, text: str):
        textbox.configure(state="normal")
        textbox.insert("end", text)
        textbox.see("end")
        textbox.configure(state="disabled")

    def _clear(self, textbox: ctk.CTkTextbox):
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.configure(state="disabled")

    def append_tx(self, text: str):
        self._append(self.txt_tx, text if text.endswith("\n") else text + "\n") 
