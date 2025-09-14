# theme.py
import customtkinter as ctk

# ===== Paleta base (claro) =====
BG_MAIN    = "#F9FAFB"
PANEL      = "#E5E7EB"
TXT        = "#111827"
ACCENT     = "#2563EB"
ACCENT_H   = "#1D4ED8"
OK_COLOR   = "#059669"
ERR_COLOR  = "#DC2626"

# ===== Botones Sidebar (modo claro) =====
SIDEBAR_BTN_BG        = "#374151"  # gris oscuro
SIDEBAR_BTN_HOVER_BG  = "#1F2937"  # gris más oscuro
SIDEBAR_BTN_FG        = "#FFFFFF"  # texto
SIDEBAR_BTN_ACTIVE_BG = "#2563EB"  # usa el ACCENT para activo
SIDEBAR_BTN_ACTIVE_H  = "#1D4ED8"

# (Opcional) tokens para KPI
KPI_TEMP = "#F59E0B"
KPI_HUM  = "#10B981"
KPI_VOLT = "#3B82F6"

# Timings
SCAN_INTERVAL_MS = 1000
RX_POLL_MS       = 50

#Titutlos
APP_TITLE = "iSebas HMI – Plantilla Modular"
APP_SIZE = "1100x680"

def setup_theme():
    ctk.set_appearance_mode("light")