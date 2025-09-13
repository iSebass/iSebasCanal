import customtkinter as ctk
from ..config import *

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=210, fg_color=PANEL, corner_radius=0)
        
        self.nav_buttons = {}
        self._create_widgets()
        
    def _create_widgets(self):
        # Título del menú
        self.lbl_menu = ctk.CTkLabel(
            self, text="MENÚ", 
            text_color=TXT, 
            font=("",14,"bold")
        )
        self.lbl_menu.pack(pady=(14,6))

    def add_nav_button(self, name, command):
        btn = ctk.CTkButton(
            self, text=name, width=180,
            fg_color="#374151", hover_color="#1F2937", 
            text_color="white",
            command=lambda: command(name)
        )
        btn.pack(padx=16, pady=6)
        self.nav_buttons[name] = btn
        
    def set_active(self, active_name):
        for name, btn in self.nav_buttons.items():
            if name == active_name:
                btn.configure(fg_color=ACCENT, hover_color=ACCENT_H)
            else:
                btn.configure(fg_color="#374151", hover_color="#1F2937")