import customtkinter as ctk
from ..config import *

class BottomBar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, height=34, fg_color=PANEL, corner_radius=0)
        
        self.lbl_info = ctk.CTkLabel(self, text="Listo.", text_color=TXT)
        self.lbl_info.pack(expand=True)
        
    def set_text(self, text):
        self.lbl_info.configure(text=text)