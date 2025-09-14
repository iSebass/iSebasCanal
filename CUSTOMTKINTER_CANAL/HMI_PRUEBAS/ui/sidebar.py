# ui/sidebar.py
import customtkinter as ctk
from ..theme import (
    PANEL, TXT,
    SIDEBAR_BTN_BG, SIDEBAR_BTN_HOVER_BG, SIDEBAR_BTN_FG,
    SIDEBAR_BTN_ACTIVE_BG, SIDEBAR_BTN_ACTIVE_H
)

class SideBar(ctk.CTkFrame):
    def __init__(self, master, on_nav, **kwargs):
        super().__init__(master, width=210, fg_color=PANEL, corner_radius=0, **kwargs)
        self.on_nav = on_nav
        self._buttons = {}     # route -> button
        self._current = None   # ruta activa

        ctk.CTkLabel(self, text="MENÚ", text_color=TXT, font=("",14,"bold")).pack(pady=(14, 8))

        self._add_nav_button("Monitor Serie", "monitor")
        self._add_nav_button("Dashboard", "dashboard")
        self._add_nav_button("Actuadores", "actuadores")
        self._add_nav_button("IoT", "iot")
        self._add_nav_button("Configuración", "settings")
        ctk.CTkLabel(self, text="").pack(fill="both", expand=True)
        self._add_nav_button("Acerca de", "about")

    def _add_nav_button(self, text: str, route: str):
        btn = ctk.CTkButton(
            self,
            text=text,
            width=180, height=36, corner_radius=8,
            fg_color=SIDEBAR_BTN_BG, hover_color=SIDEBAR_BTN_HOVER_BG,
            text_color=SIDEBAR_BTN_FG,
            command=lambda r=route: self._on_click(r)
        )
        btn.pack(fill="x", padx=14, pady=4)
        self._buttons[route] = btn
        return btn

    # Llamada cada vez que navegas (desde App -> on_nav)
    def set_active(self, route: str):
        self._current = route
        for r, b in self._buttons.items():
            if r == route:
                b.configure(fg_color=SIDEBAR_BTN_ACTIVE_BG, hover_color=SIDEBAR_BTN_ACTIVE_H)
            else:
                b.configure(fg_color=SIDEBAR_BTN_BG, hover_color=SIDEBAR_BTN_HOVER_BG)

    def _on_click(self, route: str):
        # actualiza estilos y notifica a App
        self.set_active(route)
        self.on_nav(route)
