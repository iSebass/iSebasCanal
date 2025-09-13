import customtkinter as ctk


BG_MAIN   = "#F9FAFB"
PANEL     = "#E5E7EB"
TXT       = "#111827"
ACCENT    = "#2563EB"
ACCENT_H  = "#1D4ED8"
OK_COLOR  = "#059669"
ERR_COLOR = "#DC2626"


SCAN_INTERVAL_MS = 1000 # 1 s
RX_POLL_MS       = 50 # ms

APP_TITLE = "iSebas HMI – Plantilla Modular"
APP_SIZE = "1100x680"

def setup_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
