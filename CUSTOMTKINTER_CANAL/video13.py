# -*- coding: utf-8 -*-
# video13.py (parcheado a partir de tu base)

import customtkinter as ctk
import serial
import serial.tools.list_ports as list_ports
import datetime  # FIX: necesario para timestamp

# ===== Paleta Material Light Modern =====
BG_MAIN   = "#F9FAFB"   # fondo principal
PANEL     = "#E5E7EB"   # frames/paneles
TXT       = "#111827"   # texto base
ACCENT    = "#2563EB"   # botón primario
ACCENT_H  = "#1D4ED8"   # hover
OK_COLOR  = "#059669"   # verde éxito
ERR_COLOR = "#DC2626"   # rojo error

SCAN_INTERVAL_MS = 1000  # cada 1 s
RX_POLL_MS       = 50    # RX no bloqueante

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ===== Ventana =====
        self.title("iSebas HMI - Video 13 (Monitor Serie sin congelarse)")
        self.geometry("1000x650")
        self.configure(fg_color=BG_MAIN)

        # ===== Estado Serie =====
        self.baudrates   = ["4800", "9600", "19200", "38400", "115200"]
        self.ports_cache = []
        self.port_var    = ctk.StringVar(value="")
        self.ser = None
        self._rx_after_id = None

        # ===== Variables de opciones (FIX: quitar duplicados) =====
        self.cr_lf_var = ctk.BooleanVar(value=True)
        self.ts_var    = ctk.BooleanVar(value=True)

        # ===== Buffers de log (FIX: antes no existían) =====
        self.rx_log = []
        self.tx_log = []
        self.max_log_lines = 2000

        # =================== TOP BAR ===================
        self.topbar = ctk.CTkFrame(self, height=56, fg_color=PANEL, corner_radius=0)
        self.topbar.pack(side="top", fill="x")

        self.lbl_puertos = ctk.CTkLabel(self.topbar, text="Puerto:", text_color=TXT)
        self.lbl_puertos.pack(side="left", padx=(16,6), pady=10)

        self.cbo_puertos = ctk.CTkComboBox(
            self.topbar, values=[], width=140, variable=self.port_var,
            command=self.on_port_changed
        )
        self.cbo_puertos.set("")
        self.cbo_puertos.pack(side="left", padx=(0,16), pady=10)

        self.lbl_baudrates = ctk.CTkLabel(self.topbar, text="Baudios:", text_color=TXT)
        self.lbl_baudrates.pack(side="left", padx=(0,6), pady=10)

        self.cbo_baudrates = ctk.CTkComboBox(
            self.topbar, values=self.baudrates, width=120, command=self.on_baud_changed
        )
        self.cbo_baudrates.set("9600")
        self.cbo_baudrates.pack(side="left", padx=(0,16), pady=10)

        self.lbl_estado = ctk.CTkLabel(self.topbar, text="Desconectado", text_color="gray")
        self.lbl_estado.pack(side="left", padx=(0,16), pady=10)

        self.topbar_spacer = ctk.CTkLabel(self.topbar, text="", fg_color=PANEL)
        self.topbar_spacer.pack(side="left", fill="x", expand=True)

        self.btn_connect = ctk.CTkButton(
            self.topbar, text="Conectar", width=120,
            fg_color=ACCENT, hover_color=ACCENT_H, text_color="white",
            command=self._toggle_connect
        )
        self.btn_connect.pack(side="right", padx=(8,12), pady=10)

        # ============== BODY (Sidebar + Content) ==============
        self.body = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self.body.pack(side="top", fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(self.body, width=210, fg_color=PANEL, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.lbl_menu = ctk.CTkLabel(self.sidebar, text="MENÚ", text_color=TXT, font=("",14,"bold"))
        self.lbl_menu.pack(pady=(14,6))

        self.nav_buttons = {}
        self._add_nav_button("MonitorSerie", self.show_monitor)
        self._add_nav_button("Dashboard",    self.show_dashboard)
        self._add_nav_button("Actuadores",   self.show_actuadores)
        self._add_nav_button("IoT",          self.show_iot)

        self.content = ctk.CTkFrame(self.body, fg_color=BG_MAIN)
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {
            "MonitorSerie": ctk.CTkFrame(self.content, fg_color=BG_MAIN),
            "Dashboard":    self._make_page("Dashboard"),
            "Actuadores":   self._make_page("Actuadores"),
            "IoT":          self._make_page("IoT"),
        }

        self._build_monitor_serie(self.pages["MonitorSerie"])

        for p in self.pages.values():
            p.place(relx=0, rely=0, relwidth=1, relheight=1)
            p.lower()

        # =================== BOTTOM BAR ===================
        self.bottombar = ctk.CTkFrame(self, height=34, fg_color=PANEL, corner_radius=0)
        self.bottombar.pack(side="bottom", fill="x")

        self.lbl_info_bottombar = ctk.CTkLabel(self.bottombar, text="Listo.", text_color=TXT)
        self.lbl_info_bottombar.pack(expand=True)

        # Primer escaneo + refresco periódico
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)

        # Página por defecto
        self.show_monitor()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    #====================================================================================
    # LÓGICA DEL MONITOR SERIE
    #====================================================================================
    def _build_monitor_serie(self, frame):
        ctk.CTkLabel(frame, text="Monitor Serie", text_color=TXT, font=("",16,"bold")).pack(
            padx=16, pady=(16,8), anchor="w"
        )

        # Opciones (TS / CRLF)
        opts = ctk.CTkFrame(frame, fg_color=BG_MAIN)
        opts.pack(fill="x", padx=16, pady=(0,8))

        ctk.CTkCheckBox(opts, text="ACTIVAR TIME STAMP", text_color=TXT, font=("",14,"bold"),
                        variable=self.ts_var).pack(side="left")

        ctk.CTkCheckBox(opts, text="ACTIVAR CR/LF AL ENVIAR", text_color=TXT, font=("",14,"bold"),
                        variable=self.cr_lf_var).pack(side="left", padx=10)

        # Panel de consolas (2 columnas)
        consoles = ctk.CTkFrame(frame, fg_color=PANEL, corner_radius=10)
        consoles.pack(fill="both", expand=True, padx=16, pady=(4,12))
        consoles.grid_columnconfigure(0, weight=1)
        consoles.grid_columnconfigure(1, weight=1)
        consoles.grid_rowconfigure(1, weight=1)

        # --- RX ---
        ctk.CTkLabel(consoles, text="Entradas (RX)", text_color=TXT, font=("",13,"bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10,0)
        )
        self.txt_rx = ctk.CTkTextbox(
            consoles, wrap="word", fg_color=BG_MAIN, text_color=TXT,
            font=("Consolas", 12), corner_radius=10, border_width=1, border_color=ACCENT
        )
        self.txt_rx.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.txt_rx.configure(state="disabled")

        self.btn_limpiar_rx = ctk.CTkButton(
            consoles, text="Limpiar RX", width=110,
            fg_color="#374151", hover_color="#1F2937", text_color="white",
            corner_radius=8, command=self._clear_rx
        )
        self.btn_limpiar_rx.grid(row=2, column=0, sticky="w", padx=10, pady=(0,10))

        # --- TX ---
        ctk.CTkLabel(consoles, text="Salidas (TX)", text_color=TXT, font=("",13,"bold")).grid(
            row=0, column=1, sticky="w", padx=10, pady=(10,0)
        )
        self.txt_tx = ctk.CTkTextbox(
            consoles, wrap="word", fg_color=BG_MAIN, text_color=TXT,
            font=("Consolas", 12), corner_radius=10, border_width=1, border_color=ACCENT
        )
        self.txt_tx.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.txt_tx.configure(state="disabled")

        self.btn_limpiar_tx = ctk.CTkButton(
            consoles, text="Limpiar TX", width=110,
            fg_color="#374151", hover_color="#1F2937", text_color="white",
            corner_radius=8, command=self._clear_tx
        )
        self.btn_limpiar_tx.grid(row=2, column=1, sticky="w", padx=10, pady=(0,10))

        # Línea de envío
        tx_row = ctk.CTkFrame(frame, fg_color=BG_MAIN)
        tx_row.pack(fill="x", padx=16, pady=(0,16))

        self.txt_serie = ctk.CTkEntry(
            tx_row, placeholder_text="Escribe un comando…",
            fg_color=PANEL, text_color=TXT, border_width=1, border_color=ACCENT,
            corner_radius=8, font=("", 13)
        )
        self.txt_serie.pack(side="left", fill="x", expand=True, padx=(0,8))
        self.txt_serie.bind("<Return>", lambda e: self._send_from_entry())

        self.btn_enviar = ctk.CTkButton(
            tx_row, text="Enviar", width=120,
            fg_color=ACCENT, hover_color=ACCENT_H, text_color="white",
            corner_radius=8, command=self._send_from_entry
        )
        self.btn_enviar.pack(side="left")

    def _write_to_textbox(self, textbox, text: str, stamped: bool = False):
        if textbox is None:
            return
        if stamped:
            prefix = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
            text = "".join(prefix + ln if ln.strip() else ln for ln in text.splitlines(True))
        textbox.configure(state="normal")
        textbox.insert("end", text)
        textbox.see("end")
        textbox.configure(state="disabled")

    def _append_rx(self, text: str):
        lines = text.splitlines()
        if not lines:
            return
        self.rx_log.extend(lines)
        if len(self.rx_log) > self.max_log_lines:
            del self.rx_log[:len(self.rx_log) - self.max_log_lines]

    def _append_tx(self, text: str):
        lines = text.splitlines()
        if not lines:
            return
        self.tx_log.extend(lines)
        if len(self.tx_log) > self.max_log_lines:
            del self.tx_log[:len(self.tx_log) - self.max_log_lines]

    def _clear_rx(self):
        self.rx_log.clear()
        if hasattr(self, "txt_rx"):
            self.txt_rx.configure(state="normal")
            self.txt_rx.delete("1.0", "end")
            self.txt_rx.configure(state="disabled")
        self.lbl_info_bottombar.configure(text="🧹 RX limpio.")

    def _clear_tx(self):
        self.tx_log.clear()
        if hasattr(self, "txt_tx"):
            self.txt_tx.configure(state="normal")
            self.txt_tx.delete("1.0", "end")
            self.txt_tx.configure(state="disabled")
        self.lbl_info_bottombar.configure(text="🧹 TX limpio.")

    # ----------- Envío (FIX: esta función faltaba) -----------
    def _send_from_entry(self):
        data = self.txt_serie.get()
        if not data:
            return

        payload = (data + ("\r\n" if self.cr_lf_var.get() else "")).encode("utf-8", errors="ignore")

        if self.ser and self.ser.is_open:
            try:
                self.ser.write(payload)
                self._write_to_textbox(self.txt_tx, data + "\n", stamped=self.ts_var.get())
                self._append_tx(data)
                self.txt_serie.delete(0, "end")
                self.lbl_info_bottombar.configure(text="⬆️ Enviado.")
            except Exception as e:
                self.lbl_info_bottombar.configure(text=f"❌ Error de envío: {e}")
        else:
            self.lbl_info_bottombar.configure(text="⚠️ Conéctate antes de enviar.")

    # ---------------- Navegación ----------------
    def _add_nav_button(self, name, cmd):
        btn = ctk.CTkButton(
            self.sidebar, text=name, width=180,
            fg_color="#374151", hover_color="#1F2937", text_color="white",
            command=lambda n=name, c=cmd: self._on_nav(n, c)
        )
        btn.pack(padx=16, pady=6)
        self.nav_buttons[name] = btn

    def _on_nav(self, name, cmd):
        for n, b in self.nav_buttons.items():
            if n == name:
                b.configure(fg_color=ACCENT, hover_color=ACCENT_H)
            else:
                b.configure(fg_color="#374151", hover_color="#1F2937")
        cmd()

    def _make_page(self, text):
        frame = ctk.CTkFrame(self.content, fg_color=BG_MAIN)
        ctk.CTkLabel(frame, text=text, text_color=TXT, font=("",16,"bold")).pack(padx=12, pady=12, anchor="w")
        ctk.CTkLabel(frame, text="(Placeholder — se implementará en próximos videos)", text_color="#4B5563").pack(padx=12, anchor="w")
        return frame

    def _show_page(self, key):
        for k, p in self.pages.items():
            (p.lift() if k == key else p.lower())

    def show_monitor(self):   self._on_nav("MonitorSerie", lambda: self._show_page("MonitorSerie"))
    def show_dashboard(self): self._on_nav("Dashboard",    lambda: self._show_page("Dashboard"))
    def show_actuadores(self):self._on_nav("Actuadores",   lambda: self._show_page("Actuadores"))
    def show_iot(self):       self._on_nav("IoT",          lambda: self._show_page("IoT"))

    # ---------------- RX no bloqueante ----------------
    def _start_rx_loop(self):
        if self._rx_after_id is None:
            self._rx_loop()

    def _stop_rx_loop(self):
        if self._rx_after_id is not None:
            try:
                self.after_cancel(self._rx_after_id)
            except Exception:
                pass
            self._rx_after_id = None

    def _rx_loop(self):
        try:
            if self.ser and self.ser.is_open:
                n = self.ser.in_waiting
                if n:
                    data = self.ser.read(n)
                    text = data.decode("utf-8", errors="replace")
                    # FIX: ahora sí lo llevamos al textbox RX (opcional TS) y al log
                    self._write_to_textbox(self.txt_rx, text, stamped=self.ts_var.get())
                    self._append_rx(text)
        except Exception as e:
            self.lbl_info_bottombar.configure(text=f"[RX ERROR] {e}")
        # reprogramar
        self._rx_after_id = self.after(RX_POLL_MS, self._rx_loop)

    # ---------------- Cierre ordenado ----------------
    def _on_close(self):
        try:
            self._stop_rx_loop()
        finally:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.close()
            finally:
                self.destroy()

    # ---------------- Escaneo de puertos ----------------
    def _get_ports(self):
        return [p.device for p in list_ports.comports()]

    def _scan_ports_once(self):
        ports = self._get_ports()
        if ports != self.ports_cache:
            self.ports_cache = ports[:]
            current = self.port_var.get()
            self.cbo_puertos.configure(values=ports)

            if current in ports:
                self.port_var.set(current)
            else:
                self.port_var.set(ports[0] if ports else "")
                if current and current not in ports:
                    self.lbl_info_bottombar.configure(text=f"El puerto '{current}' ya no está disponible.")
            if not ports:
                self.lbl_info_bottombar.configure(text="No hay puertos disponibles.")

    def _scan_ports_periodic(self):
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)

    # ---------------- Callbacks UI ----------------
    def on_port_changed(self, value: str):
        self.lbl_info_bottombar.configure(text=f"Puerto seleccionado: {value}")

    def on_baud_changed(self, value: str):
        self.lbl_info_bottombar.configure(text=f"Baudrate seleccionado: {value}")

    # ---------------- Conexión / Desconexión ----------------
    def _toggle_connect(self):
        if self.ser and self.ser.is_open:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        port = self.port_var.get().strip()
        try:
            baud = int(self.cbo_baudrates.get())
        except ValueError:
            self.lbl_info_bottombar.configure(text="⚠️ Baudrate inválido.")
            return

        if not port:
            self.lbl_info_bottombar.configure(text="⚠️ Selecciona un puerto.")
            return

        try:
            self.ser = serial.Serial(port=port, baudrate=baud, timeout=0.1)
        except Exception as e:
            self.lbl_info_bottombar.configure(text=f"❌ Error al abrir {port}: {e}")
            self.ser = None
            return

        self.lbl_estado.configure(text=f"Conectado", text_color=OK_COLOR)
        self.btn_connect.configure(text="Desconectar", fg_color=ERR_COLOR, hover_color="#991B1B")
        self.cbo_puertos.configure(state="disabled")
        self.cbo_baudrates.configure(state="disabled")
        self.lbl_info_bottombar.configure(text=f"✅ Conectado a {port} @ {baud} bps")

        self._start_rx_loop()

    def _disconnect(self):
        self._stop_rx_loop()

        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

        self.lbl_estado.configure(text="Desconectado", text_color="gray")
        self.btn_connect.configure(text="Conectar", fg_color=ACCENT, hover_color=ACCENT_H)
        self.cbo_puertos.configure(state="normal")
        self.cbo_baudrates.configure(state="normal")
        self.lbl_info_bottombar.configure(text="🔌 Desconectado")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = App()
    app.mainloop()
