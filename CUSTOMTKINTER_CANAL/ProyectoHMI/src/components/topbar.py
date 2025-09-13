import customtkinter as ctk
from ..config import *

class TopBar(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=56, fg_color=PANEL, corner_radius=0)
        
        self.port_var = kwargs.get('port_var')
        self.on_port_changed = kwargs.get('on_port_changed')
        self.on_baud_changed = kwargs.get('on_baud_changed')
        self.on_connect = kwargs.get('on_connect')
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Puerto
        self.lbl_puertos = ctk.CTkLabel(self, text="Puerto:", text_color=TXT)
        self.lbl_puertos.pack(side="left", padx=(16,6), pady=10)

        self.cbo_puertos = ctk.CTkComboBox(
            self, values=[], width=140, variable=self.port_var,
            command=self.on_port_changed
        )
        self.cbo_puertos.set("")
        self.cbo_puertos.pack(side="left", padx=(0,16), pady=10)

        # Baudrate
        self.lbl_baudrates = ctk.CTkLabel(self, text="Baudios:", text_color=TXT)
        self.lbl_baudrates.pack(side="left", padx=(0,6), pady=10)

        self.cbo_baudrates = ctk.CTkComboBox(
            self, values=BAUDRATES, width=120, command=self.on_baud_changed
        )
        self.cbo_baudrates.set("9600")
        self.cbo_baudrates.pack(side="left", padx=(0,16), pady=10)

        # Estado
        self.lbl_estado = ctk.CTkLabel(self, text="Desconectado", text_color="gray")
        self.lbl_estado.pack(side="left", padx=(0,16), pady=10)

        # Espaciador
        self.spacer = ctk.CTkLabel(self, text="", fg_color=PANEL)
        self.spacer.pack(side="left", fill="x", expand=True)

        # Botón conectar
        self.btn_connect = ctk.CTkButton(
            self, text="Conectar", width=120,
            fg_color=ACCENT, hover_color=ACCENT_H, text_color="white",
            command=self.on_connect
        )
        self.btn_connect.pack(side="right", padx=(8,12), pady=10)