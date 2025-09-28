# ============================
# hmi/ui/topbar.py
# ============================
import customtkinter as ctk
from ..theme import PANEL, TXT, ACCENT, ACCENT_H, OK_COLOR, ERR_COLOR


class TopBar(ctk.CTkFrame):
    def __init__(self, master, serial_manager, on_connect_toggled, on_status, **kwargs):
        super().__init__(master, height=56, fg_color=PANEL, corner_radius=0, **kwargs)
        self.serial = serial_manager
        self.on_connect_toggled = on_connect_toggled
        self.on_status = on_status

        ctk.CTkLabel(self, text="Puerto:", text_color=TXT).pack(side="left", padx=(16, 6), pady=10)

        self.port_var = ctk.StringVar(value="")
        self.cbo_puertos = ctk.CTkComboBox(self, values=[], width=140, variable=self.port_var,
                                           command=lambda v: self.on_status(f"Puerto seleccionado: {v}"))
        self.cbo_puertos.set("")
        self.cbo_puertos.pack(side="left", padx=(0, 16), pady=10)

        ctk.CTkLabel(self, text="Baudios:", text_color=TXT).pack(side="left", padx=(0, 6), pady=10)
        self.cbo_baud = ctk.CTkComboBox(self, values=["4800", "9600", "19200", "38400", "115200"], width=120,
                                        command=lambda v: self.on_status(f"Baudrate seleccionado: {v}"))
        self.cbo_baud.set("9600")
        self.cbo_baud.pack(side="left", padx=(0, 16), pady=10)

        self.lbl_estado = ctk.CTkLabel(self, text="Desconectado", text_color="gray")
        self.lbl_estado.pack(side="left", padx=(0, 16), pady=10)

        ctk.CTkLabel(self, text="", fg_color=PANEL).pack(side="left", fill="x", expand=True)

        self.btn_connect = ctk.CTkButton(self, text="Conectar", width=120, fg_color=ACCENT,
                                         hover_color=ACCENT_H, text_color="white",
                                         command=self.on_connect_toggled)
        self.btn_connect.pack(side="right", padx=(8, 12), pady=10)

    # API de estado
    def set_connected(self, connected: bool):
        if connected:
            self.lbl_estado.configure(text="Conectado", text_color=OK_COLOR)
            self.btn_connect.configure(text="Desconectar", fg_color=ERR_COLOR, hover_color="#991B1B")
            self.cbo_puertos.configure(state="disabled")
            self.cbo_baud.configure(state="disabled")
        else:
            self.lbl_estado.configure(text="Desconectado", text_color="gray")
            self.btn_connect.configure(text="Conectar", fg_color=ACCENT, hover_color=ACCENT_H)
            self.cbo_puertos.configure(state="normal")
            self.cbo_baud.configure(state="normal")

    def update_ports(self, ports: list[str]):
        current = self.port_var.get()
        self.cbo_puertos.configure(values=ports)
        if current in ports:
            self.port_var.set(current)
        else:
            self.port_var.set(ports[0] if ports else "")
            if current and current not in ports:
                self.on_status(f"El puerto '{current}' ya no está disponible.")
        if not ports:
            self.on_status("No hay puertos disponibles.")

    def get_selected_port_and_baud(self) -> tuple[str, int] | tuple[None, None]:
        port = self.port_var.get().strip()
        try:
            baud = int(self.cbo_baud.get())
        except ValueError:
            return None, None
        return port, baud