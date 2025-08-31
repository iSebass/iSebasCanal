import customtkinter as ctk
import serial
import serial.tools.list_ports as list_ports

# ===== Paleta Material Light Modern =====
BG_MAIN   = "#F9FAFB"
PANEL     = "#E5E7EB"
TXT       = "#111827"
ACCENT    = "#2563EB"
ACCENT_H  = "#1D4ED8"
OK_COLOR  = "#059669"
ERR_COLOR = "#DC2626"

SCAN_INTERVAL_MS = 1000  # cada 1 s

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ventana
        self.title("iSebas Video 06")
        self.geometry("1000x650")
        self.configure(fg_color=BG_MAIN)

        # Estado / datos base
        self.baudrates   = ["4800", "9600", "19200", "38400", "115200"]
        self.ports_cache = []                  # cache para detectar cambios
        self.port_var    = ctk.StringVar(value="")  # puerto seleccionado

        # =================== TOP BAR ===================
        self.topbar = ctk.CTkFrame(self, height=56, fg_color=PANEL, corner_radius=0)
        self.topbar.pack(side="top", fill="x")

        self.lbl_puertos = ctk.CTkLabel(self.topbar, text="Puerto:", text_color=TXT)
        self.lbl_puertos.pack(side="left", padx=(16,6), pady=10)

        # ComboBox Puerto (variable + callback)
        self.cbo_puertos = ctk.CTkComboBox(
            self.topbar, values=[], width=180,
            variable=self.port_var,           # <— importante
            command=self.on_port_changed
        )
        self.cbo_puertos.pack(side="left", padx=(0,16), pady=10)

        self.lbl_baudrates = ctk.CTkLabel(self.topbar, text="Baudios:", text_color=TXT)
        self.lbl_baudrates.pack(side="left", padx=(0,6), pady=10)

        self.cbo_baudrates = ctk.CTkComboBox(
            self.topbar, values=self.baudrates, width=120,
            command=self.on_baud_changed
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
            command=self._toggle_button_demo
        )
        self.btn_connect.pack(side="right", padx=(8,12), pady=10)

        # ============== BODY (Sidebar + Content) ==============
        self.body = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self.body.pack(side="top", fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(self.body, width=210, fg_color=PANEL, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.lbl_menu = ctk.CTkLabel(self.sidebar, text="MENÚ", text_color=TXT, font=("", 14, "bold"))
        self.lbl_menu.pack(pady=(14,6), padx=50)

        self.content = ctk.CTkFrame(self.body, fg_color=BG_MAIN)
        self.content.pack(side="left", fill="both", expand=True)

        self.lbl_content = ctk.CTkLabel(self.content, text="Contenido principal", text_color=TXT, font=("", 16, "bold"))
        self.lbl_content.pack(padx=12, pady=12)

        # =================== BOTTOM BAR ===================
        self.bottombar = ctk.CTkFrame(self, height=34, fg_color=PANEL, corner_radius=0)
        self.bottombar.pack(side="bottom", fill="x")

        self.lbl_info_bottombar = ctk.CTkLabel(self.bottombar, text="Listo.", text_color=TXT)
        self.lbl_info_bottombar.pack(expand=True)  # centrado

        # ---- Primer escaneo + refresco periódico ----
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)

    # ====== Escaneo de puertos ======
    def _get_ports(self):
        """Retorna lista de nombres de dispositivo (COMx, /dev/ttyUSBx, etc.)."""
        return [p.device for p in list_ports.comports()]

    def _scan_ports_once(self):
        ports = self._get_ports()
        if ports != self.ports_cache:
            self.ports_cache = ports[:]  # guarda nuevo snapshot
            current = self.port_var.get()

            # actualiza opciones del combobox
            self.cbo_puertos.configure(values=ports)

            if current in ports:
                # conserva selección actual
                self.port_var.set(current)
            else:
                # selecciona el primero disponible o vacío
                self.port_var.set(ports[0] if ports else "")
                if current and current not in ports:
                    self.lbl_info_bottombar.configure(text=f"El puerto '{current}' ya no está disponible.")

            # Si no hay puertos, avisa
            if not ports:
                self.lbl_info_bottombar.configure(text="No hay puertos disponibles.")

    def _scan_ports_periodic(self):
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)

    # ======= Callbacks / Helpers =======
    def on_port_changed(self, value: str):
        self.lbl_info_bottombar.configure(text=f"Puerto seleccionado: {value}")

    def on_baud_changed(self, value: str):
        self.lbl_info_bottombar.configure(text=f"Baudios seleccionados: {value}")

    def _toggle_button_demo(self):
        """Demostración visual (sin lógica de conexión real)."""
        if self.btn_connect.cget("text") == "Conectar":
            self.btn_connect.configure(text="Desconectar", fg_color=ERR_COLOR, hover_color="#991B1B")
            self.lbl_estado.configure(text="Conectado", text_color=OK_COLOR)
            self.lbl_info_bottombar.configure(
                text=f"Conectado a {self.port_var.get()} @ {self.cbo_baudrates.get()} bps"
            )
        else:
            self.btn_connect.configure(text="Conectar", fg_color=ACCENT, hover_color=ACCENT_H)
            self.lbl_estado.configure(text="Desconectado", text_color="gray")
            self.lbl_info_bottombar.configure(text="Desconectado")

if __name__ == "__main__":
    app = App()
    app.mainloop()
