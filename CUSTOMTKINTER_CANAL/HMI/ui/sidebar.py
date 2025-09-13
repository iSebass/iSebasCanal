# ============================
# hmi/ui/sidebar.py
# ============================
import customtkinter as ctk
from ..theme import PANEL, TXT, ACCENT, ACCENT_H


class SideBar(ctk.CTkFrame):
    def __init__(self, master, on_nav, **kwargs):
        super().__init__(master, width=210, fg_color=PANEL, corner_radius=0, **kwargs)
        self.on_nav = on_nav

        ctk.CTkLabel(self, text="MENÚ", text_color=TXT, font=("", 14, "bold")).pack(pady=(14, 8))

        self._add_nav_button("Monitor Serie", "monitor")
        self._add_nav_button("Dashboard", "dashboard")
        self._add_nav_button("Actuadores", "actuadores")
        self._add_nav_button("IoT", "iot")
        self._add_nav_button("Configuración", "settings")
        self._add_nav_button("iSebas", "isebas")
        ctk.CTkLabel(self, text="", fg_color=PANEL).pack(fill="both", expand=True)
        self._add_nav_button("Acerca de", "about")

    def _add_nav_button(self, text: str, route: str):
        btn = ctk.CTkButton(self, text=text, fg_color=ACCENT, hover_color=ACCENT_H,
                            text_color="white", corner_radius=8, height=36,
                            command=lambda r=route: self.on_nav(r))
        btn.pack(fill="x", padx=14, pady=6)
