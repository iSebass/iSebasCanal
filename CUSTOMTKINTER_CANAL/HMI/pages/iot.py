# ============================
# hmi/pages/iot.py
# ============================
import customtkinter as ctk
from .base import BasePage
from ..theme import PANEL


class IoTPage(BasePage):
    title = "IoT"
    subtitle = "MQTT / EMQX / Dashboard web (plantilla)"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        box = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=12)
        box.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(box, text="Aquí irán campos de broker, topics, botones de publicar/suscribir.").pack(pady=18)

