# ============================
# hmi/pages/about.py
# ============================
import customtkinter as ctk
from .base import BasePage
from ..theme import PANEL


class AboutPage(BasePage):
    title = "Acerca de"
    subtitle = "Información de la HMI"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        box = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=12)
        box.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(box, text="iSebas HMI – Plantilla para videos del canal.").pack(pady=18)

