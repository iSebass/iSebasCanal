# HMI/pages/dashboard.py
import customtkinter as ctk
from .base import BasePage
from ..theme import PANEL, BG_MAIN, TXT

# ===== Paleta (fallbacks si no tienes tokens en theme.py) =====
KPI_TEMP = "#7C3AED"  # morado
KPI_HUM  = "#10B981"  # verde
KPI_VOLT = "#3B82F6"  # azul

CARD_BG   = "#FFFFFF"
RADIUS    = 16
PAD       = 12


class SensorCard(ctk.CTkFrame):
    
    def __init__(self, master, title: str, header_color: str,
                 icon_top: str, icon_bottom: str,
                 value_var: ctk.StringVar, unit: str, **kwargs):
        super().__init__(master, fg_color=CARD_BG, corner_radius=RADIUS, **kwargs)

        # Header (tira superior)
        header = ctk.CTkFrame(self, fg_color=header_color, corner_radius=RADIUS, height=36)
        header.pack(fill="x", padx=PAD, pady=(PAD, 6))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text=icon_top, font=("Segoe UI Emoji", 24), text_color="white")\
            .pack(side="left", padx=(10, 8))
        ctk.CTkLabel(header, text=title, font=("", 14, "bold"), text_color="white")\
            .pack(side="left")

        # Cuerpo
        body = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=RADIUS)
        body.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))

        # Valor grande
        row = ctk.CTkFrame(body, fg_color=CARD_BG)
        row.pack(fill="x", pady=(2, 2))
        ctk.CTkLabel(row, textvariable=value_var, text_color=TXT, font=("", 24, "bold"))\
            .pack(side="left")
        ctk.CTkLabel(row, text=f" {unit}", text_color=TXT, font=("", 12))\
            .pack(side="left")

        # Icono inferior (decorativo)
        ctk.CTkLabel(body, text=icon_bottom, font=("Segoe UI Emoji", 22))\
            .pack(anchor="w", padx=2, pady=(6, 0))

class DashboardPage(BasePage):
    title = "Dashboard"
    subtitle = "Visión general del sistema"

    def __init__(self, master,  **kwargs):
        super().__init__(master, **kwargs)

        # ===== Variables (lo que se muestra en las tarjetas) =====
        self.temp_var = ctk.StringVar(value="0.0")
        self.hum_var  = ctk.StringVar(value="0.0")
        self.volt_var = ctk.StringVar(value="0.0")

        #Agregar nuevos sensores
        
        # ===== Contenedor de tarjetas =====
        self.sensor_grid = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.sensor_grid.pack(fill="both", expand=True, padx=16, pady=16)
        self.sensor_grid.grid_columnconfigure( (0, 1, 2), weight=1, uniform="a")
        self.sensor_grid.grid_rowconfigure(0, weight=0)

        # ===== Tarjetas (estructura limpia; puedes cambiar colores luego) =====
        self.card_temp = SensorCard(
            self.sensor_grid, "Temp", KPI_TEMP, "🌡️", "🌡️",
            value_var=self.temp_var, unit="°C"
        )
        self.card_hum = SensorCard(
            self.sensor_grid, "Hum", KPI_HUM, "💧", "🌧️",
            value_var=self.hum_var, unit="%"
        )
        self.card_volt = SensorCard(
            self.sensor_grid, "Volt", KPI_VOLT, "🔌", "⚡",
            value_var=self.volt_var, unit="V"
        )
        #CARTAS ADICIONALES
        
        #ORGANIZAMOS LAS TARJETAS EN EL FRAME
        self.card_temp.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.card_hum.grid( row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.card_volt.grid(row=0, column=2, sticky="nsew", padx=8, pady=8)

        #AGREGAMOS AL GRID LAS NUEVAS CARTAS
        
        #AGREGAR CONTENEDOR DE GRAFICOS
        

    # ===== Helpers =====
    @staticmethod
    def _fmt(v):
        try:
            return f"{float(v):.2f}"
        except Exception:
            return str(v)

    # ===== Setters (llámalos desde el Monitor) =====
    def set_temperature_val(self, value):
        self.temp_var.set(self._fmt(value))

    def set_humidity_val(self, value):
        self.hum_var.set(self._fmt(value))

    def set_voltage_val(self, value):
        self.volt_var.set(self._fmt(value))

   