# ============================
# hmi/pages/dashboard.py
# ============================
import customtkinter as ctk
from .base import BasePage
from ..theme import PANEL


class DashboardPage(BasePage):
    title = "Dashboard"
    subtitle = "Visión general del sistema"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        grid = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=12)
        grid.pack(fill="both", expand=True, padx=16, pady=16)
        grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")
        grid.grid_rowconfigure((0, 1), weight=1, uniform="a")

        for i in range(2):
            for j in range(3):
                card = ctk.CTkFrame(grid, fg_color="#FFFFFF", corner_radius=12)
                card.grid(row=i, column=j, padx=10, pady=10, sticky="nsew")
                ctk.CTkLabel(card, text=f"Card {i*3+j+1}").pack(pady=16)