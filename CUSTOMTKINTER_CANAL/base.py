import customtkinter as ctk
import serial
import serial.tools.list_ports as list_ports
from tkinter import filedialog
import datetime

# ===== Paleta =====
BG_MAIN   = "#F9FAFB"
PANEL     = "#E5E7EB"
TXT       = "#111827"
ACCENT    = "#2563EB"
ACCENT_H  = "#1D4ED8"
OK_COLOR  = "#059669"
ERR_COLOR = "#DC2626"

SCAN_INTERVAL_MS = 1000
RX_POLL_MS       = 50

# ========================= PÁGINAS =========================
class MonitorSeriePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN)
        self.app = app

        self.lbl_title = ctk.CTkLabel(
            self, 
            text="Monitor Serie", 
            text_color=TXT, 
            font=("", 16, "bold")
        )
        self.lbl_title.pack(padx=12, pady=(12,8), anchor="w")

        opts = ctk.CTkFrame(self, fg_color=BG_MAIN)
        opts.pack(fill="x", padx=12, pady=(0,8))
        
        self.chk_ts_var = app.chk_ts_var   # comparte con app para coherencia si quieres
        self.chk_crlf_var = app.chk_crlf_var
        self.chk_ts = ctk.CTkCheckBox(opts, text="Timestamp RX", variable=self.chk_ts_var, text_color=TXT)
        self.chk_ts.pack(side="left", padx=(0,12))
        self.chk_crlf = ctk.CTkCheckBox(opts, text="Añadir \\r\\n al enviar", variable=self.chk_crlf_var, text_color=TXT)
        self.chk_crlf.pack(side="left")

        self.txt_console = ctk.CTkTextbox(self, fg_color="white", text_color="#111827", wrap="word")
        self.txt_console.pack(padx=12, pady=(0,8), fill="both", expand=True)
        self.txt_console.configure(state="disabled")

        send_row = ctk.CTkFrame(self, fg_color=BG_MAIN)
        send_row.pack(fill="x", padx=12, pady=(0,12))
        self.entry_send = ctk.CTkEntry(send_row, placeholder_text="Escribe comando…")
        self.entry_send.pack(side="left", fill="x", expand=True)
        self.btn_send = ctk.CTkButton(send_row, text="Enviar", width=110, command=self._send_line)
        self.btn_send.pack(side="left", padx=(8,0))

        # Accesos desde app
        app.console_append = self._console_append  # asigna callback
        app.console_widget = self.txt_console
        app.entry_send     = self.entry_send

    def _console_append(self, text: str):
        self.txt_console.configure(state="normal")
        self.txt_console.insert("end", text)
        self.txt_console.see("end")
        self.txt_console.configure(state="disabled")
        self.app.log_buffer.append(text)

    def _send_line(self):
        line = self.entry_send.get()
        if not line:
            return
        to_send = line + ("\r\n" if self.chk_crlf_var.get() else "")
        try:
            if self.app.ser and self.app.ser.is_open:
                self.app.ser.write(to_send.encode("utf-8"))
                stamp = f"[{self.app.stamp()}] " if self.chk_ts_var.get() else ""
                self._console_append(f"{stamp}>> {line}\n")
                self.entry_send.delete(0, "end")
            else:
                self.app.set_status("⚠️ No hay conexión activa.")
        except Exception as e:
            self.app.set_status(f"❌ Error al enviar: {e}")


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN)
        ctk.CTkLabel(self, text="Dashboard (placeholder)", text_color=TXT, font=("", 16, "bold")).pack(padx=12, pady=12, anchor="w")
        ctk.CTkLabel(self, text="Aquí montaremos gráficos en vivo y KPIs de sensores.", text_color=TXT).pack(padx=12, anchor="w")


class ActuadoresPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN)
        self.app = app
        ctk.CTkLabel(self, text="Actuadores", text_color=TXT, font=("", 16, "bold")).pack(padx=12, pady=12, anchor="w")

        grid = ctk.CTkFrame(self, fg_color=BG_MAIN)
        grid.pack(padx=12, pady=8, fill="x")

        self.tg1 = ToggleActuador(grid, app, "LED 1", "LED1 ON", "LED1 OFF")
        self.tg1.grid(row=0, column=0, padx=6, pady=6, sticky="w")

        self.tg2 = ToggleActuador(grid, app, "Bomba", "PUMP ON", "PUMP OFF")
        self.tg2.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ctk.CTkLabel(self, text="Sugerencia: define aquí tus comandos y mapeos para el firmware.", text_color="#4B5563").pack(padx=12, pady=(6,0), anchor="w")


class ToggleActuador(ctk.CTkFrame):
    def __init__(self, master, app, label, cmd_on, cmd_off):
        super().__init__(master, fg_color=PANEL, corner_radius=10)
        self.app = app
        self.cmd_on = cmd_on
        self.cmd_off = cmd_off
        self.state = False

        ctk.CTkLabel(self, text=label, text_color=TXT, font=("", 13, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.btn = ctk.CTkButton(self, text="OFF", width=90, fg_color=ERR_COLOR, hover_color="#991B1B", command=self.toggle)
        self.btn.grid(row=0, column=1, padx=10, pady=10)

    def toggle(self):
        self.state = not self.state
        cmd = self.cmd_on if self.state else self.cmd_off
        self._send(cmd)
        if self.state:
            self.btn.configure(text="ON", fg_color=OK_COLOR, hover_color="#047857")
        else:
            self.btn.configure(text="OFF", fg_color=ERR_COLOR, hover_color="#991B1B")

    def _send(self, line: str):
        to_send = line + ("\r\n" if self.app.chk_crlf_var.get() else "")
        try:
            if self.app.ser and self.app.ser.is_open:
                self.app.ser.write(to_send.encode("utf-8"))
                if hasattr(self.app, "console_append"):
                    stamp = f"[{self.app.stamp()}] " if self.app.chk_ts_var.get() else ""
                    self.app.console_append(f"{stamp}>> {line}\n")
            else:
                self.app.set_status("⚠️ No hay conexión activa.")
        except Exception as e:
            self.app.set_status(f"❌ Error al enviar: {e}")


class IoTPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=BG_MAIN)
        ctk.CTkLabel(self, text="IoT (placeholder)", text_color=TXT, font=("", 16, "bold")).pack(padx=12, pady=12, anchor="w")
        ctk.CTkLabel(
            self,
            text="Aquí configuraremos MQTT (broker, topics, QoS) y un panel para publicar/subscribir.",
            text_color=TXT
        ).pack(padx=12, anchor="w")


# ========================= APP PRINCIPAL =========================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ventana
        self.title("iSebas HMI - Video 11")
        self.geometry("1100x700")
        self.configure(fg_color=BG_MAIN)

        # Estado serie
        self.baudrates   = ["4800", "9600", "19200", "38400", "115200"]
        self.ports_cache = []
        self.port_var    = ctk.StringVar(value="")
        self.ser: serial.Serial | None = None
        self._rx_after_id = None

        # Preferencias compartidas
        self.chk_ts_var = ctk.BooleanVar(value=True)
        self.chk_crlf_var = ctk.BooleanVar(value=True)

        # Log
        self.log_buffer = []

        # =================== TOP BAR ===================
        self.topbar = ctk.CTkFrame(self, height=56, fg_color=PANEL, corner_radius=0)
        self.topbar.pack(side="top", fill="x")

        ctk.CTkLabel(self.topbar, text="Puerto:", text_color=TXT).pack(side="left", padx=(16,6), pady=10)
        self.cbo_puertos = ctk.CTkComboBox(self.topbar, values=[], width=160, variable=self.port_var, command=self.on_port_changed)
        self.cbo_puertos.set("")
        self.cbo_puertos.pack(side="left", padx=(0,16), pady=10)

        ctk.CTkLabel(self.topbar, text="Baudios:", text_color=TXT).pack(side="left", padx=(0,6), pady=10)
        self.cbo_baudrates = ctk.CTkComboBox(self.topbar, values=self.baudrates, width=140, command=self.on_baud_changed)
        self.cbo_baudrates.set("9600")
        self.cbo_baudrates.pack(side="left", padx=(0,16), pady=10)

        self.lbl_estado = ctk.CTkLabel(self.topbar, text="Desconectado", text_color="gray")
        self.lbl_estado.pack(side="left", padx=(0,16), pady=10)

        ctk.CTkLabel(self.topbar, text="", fg_color=PANEL).pack(side="left", fill="x", expand=True)

        self.btn_save = ctk.CTkButton(self.topbar, text="Guardar log…", width=130, fg_color="#374151", hover_color="#1F2937", text_color="white", command=self._save_log)
        self.btn_save.pack(side="right", padx=(8,8), pady=10)

        self.btn_connect = ctk.CTkButton(self.topbar, text="Conectar", width=130, fg_color=ACCENT, hover_color=ACCENT_H, text_color="white", command=self._toggle_connect)
        self.btn_connect.pack(side="right", padx=(8,12), pady=10)

        # =================== BODY ===================
        self.body = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self.body.pack(side="top", fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.body, width=220, fg_color=PANEL, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="SECCIONES", text_color=TXT, font=("", 14, "bold")).pack(pady=(14,10))

        self.nav_buttons = {}
        self._add_nav_button("MonitorSerie", self.show_monitor)
        self._add_nav_button("Dashboard", self.show_dashboard)
        self._add_nav_button("Actuadores", self.show_actuadores)
        self._add_nav_button("IoT", self.show_iot)

        # Contenedor de páginas
        self.content = ctk.CTkFrame(self.body, fg_color=BG_MAIN)
        self.content.pack(side="left", fill="both", expand=True)

        # Instancias de páginas
        self.pages = {
            "MonitorSerie": MonitorSeriePage(self.content, self),
            "Dashboard":    DashboardPage(self.content, self),
            "Actuadores":   ActuadoresPage(self.content, self),
            "IoT":          IoTPage(self.content, self),
        }
        for p in self.pages.values():
            p.place(relx=0, rely=0, relwidth=1, relheight=1)
            p.lower()

        # Bottom bar
        self.bottombar = ctk.CTkFrame(self, height=34, fg_color=PANEL, corner_radius=0)
        self.bottombar.pack(side="bottom", fill="x")
        self.lbl_info_bottombar = ctk.CTkLabel(self.bottombar, text="Listo.", text_color=TXT)
        self.lbl_info_bottombar.pack(expand=True)

        # Inicialización
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)
        self.show_monitor()  # página por defecto

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- Navegación ----------
    def _add_nav_button(self, name, cmd):
        btn = ctk.CTkButton(self.sidebar, text=name, width=180, fg_color="#374151", hover_color="#1F2937",
                            text_color="white", command=lambda n=name, c=cmd: self._on_nav(n, c))
        btn.pack(padx=16, pady=6)
        self.nav_buttons[name] = btn

    def _on_nav(self, name, cmd):
        for n, b in self.nav_buttons.items():
            if n == name:
                b.configure(fg_color=ACCENT, hover_color=ACCENT_H)
            else:
                b.configure(fg_color="#374151", hover_color="#1F2937")
        cmd()

    def _show_page(self, key):
        for k, p in self.pages.items():
            if k == key:
                p.lift()
            else:
                p.lower()

    def show_monitor(self):   self._on_nav("MonitorSerie", lambda: self._show_page("MonitorSerie"))
    def show_dashboard(self): self._on_nav("Dashboard",    lambda: self._show_page("Dashboard"))
    def show_actuadores(self):self._on_nav("Actuadores",   lambda: self._show_page("Actuadores"))
    def show_iot(self):       self._on_nav("IoT",          lambda: self._show_page("IoT"))

    # ---------- Utilidades compartidas ----------
    def set_status(self, text): self.lbl_info_bottombar.configure(text=text)
    def stamp(self): return datetime.datetime.now().strftime("%H:%M:%S")

    def _save_log(self):
        if not self.log_buffer:
            self.set_status("No hay datos para guardar.")
            return
        filename = filedialog.asksaveasfilename(title="Guardar log", defaultextension=".txt",
                                                filetypes=[("Texto", "*.txt")])
        if not filename: return
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(self.log_buffer)
            self.set_status(f"💾 Log guardado en: {filename}")
        except Exception as e:
            self.set_status(f"❌ No se pudo guardar: {e}")

    # ---------- RX loop ----------
    def _start_rx_loop(self):
        if self._rx_after_id is None:
            self._rx_loop()

    def _stop_rx_loop(self):
        if self._rx_after_id is not None:
            try: self.after_cancel(self._rx_after_id)
            except Exception: pass
            self._rx_after_id = None

    def _rx_loop(self):
        try:
            if self.ser and self.ser.is_open:
                n = self.ser.in_waiting
                if n:
                    data = self.ser.read(n)
                    text = data.decode("utf-8", errors="replace")
                    # si existe consola (página activa o no), se registra
                    if hasattr(self, "console_append"):
                        if self.chk_ts_var.get():
                            for line in text.splitlines(True):
                                self.console_append(f"[{self.stamp()}] {line}")
                        else:
                            self.console_append(text)
        except Exception as e:
            if hasattr(self, "console_append"):
                self.console_append(f"[RX ERROR] {e}\n")

        self._rx_after_id = self.after(RX_POLL_MS, self._rx_loop)

    # ---------- Serial ----------
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
                    self.set_status(f"El puerto '{current}' ya no está disponible.")
            if not ports:
                self.set_status("No hay puertos disponibles.")

    def _scan_ports_periodic(self):
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)

    def on_port_changed(self, value: str):
        self.set_status(f"Puerto seleccionado: {value}")

    def on_baud_changed(self, value: str):
        self.set_status(f"Baudrate seleccionado: {value}")

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
            self.set_status("⚠️ Baudrate inválido.")
            return
        if not port:
            self.set_status("⚠️ Selecciona un puerto.")
            return
        try:
            self.ser = serial.Serial(port=port, baudrate=baud, timeout=0.1)
        except Exception as e:
            self.set_status(f"❌ Error al abrir {port}: {e}")
            self.ser = None
            return

        self.lbl_estado.configure(text="Conectado", text_color=OK_COLOR)
        self.btn_connect.configure(text="Desconectar", fg_color=ERR_COLOR, hover_color="#991B1B")
        self.cbo_puertos.configure(state="disabled")
        self.cbo_baudrates.configure(state="disabled")
        self.set_status(f"✅ Conectado a {port} @ {baud} bps")
        self._start_rx_loop()

    def _disconnect(self):
        self._stop_rx_loop()
        if self.ser:
            try: self.ser.close()
            except Exception: pass
            self.ser = None

        self.lbl_estado.configure(text="Desconectado", text_color="gray")
        self.btn_connect.configure(text="Conectar", fg_color=ACCENT, hover_color=ACCENT_H)
        self.cbo_puertos.configure(state="normal")
        self.cbo_baudrates.configure(state="normal")
        self.set_status("🔌 Desconectado")

    # ---------- Cerrar ----------
    def _on_close(self):
        try:
            self._stop_rx_loop()
        finally:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.close()
            finally:
                self.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = App()
    app.mainloop()
