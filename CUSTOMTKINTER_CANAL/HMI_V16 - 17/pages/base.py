# ============================
# hmi/pages/base.py
# ============================
import customtkinter as ctk
from ..theme import BG_MAIN, TXT


class BasePage(ctk.CTkFrame):
    """Página base con utilidades comunes."""

    title = "Página"
    subtitle = "En construcción"

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, **kwargs)
        self._build_header()

    def _build_header(self):
        ctk.CTkLabel(self, text=self.title, text_color=TXT, font=("", 18, "bold")) \
            .pack(padx=16, pady=(16, 0), anchor="w")
        ctk.CTkLabel(self, text=self.subtitle, text_color=TXT, font=("", 13)) \
            .pack(padx=16, pady=(0, 12), anchor="w")