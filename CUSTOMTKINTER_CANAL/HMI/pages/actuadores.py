# ============================
# hmi/pages/actuadores.py
# ============================
import customtkinter as ctk
from .base import BasePage
from ..theme import PANEL


class ActuadoresPage(BasePage):
    title = "Actuadores"
    subtitle = "Control de salidas y PWM (plantilla)"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        box = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=12)
        box.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(box, text="Aquí irán switches/botones para relés, PWM, servos, etc.").pack(pady=18)
