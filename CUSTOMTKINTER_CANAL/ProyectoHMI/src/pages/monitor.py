import customtkinter as ctk
from ..config import *

class MonitorPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=BG_MAIN)
        
        self.cr_lf_var = kwargs.get('cr_lf_var', ctk.BooleanVar(value=True))
        self.ts_var = kwargs.get('ts_var', ctk.BooleanVar(value=True))
        self.send_callback = kwargs.get('send_callback')
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Título
        ctk.CTkLabel(
            self, text="Monitor Serie", 
            text_color=TXT, 
            font=("", 18, "bold")
        ).pack(padx=16, pady=(16, 8), anchor="w")
        
        # Opciones
        self._create_options()
        
        # Consola
        self._create_console()
        
        # Línea de envío
        self._create_send_line()
        
    def _create_options(self):
        opts = ctk.CTkFrame(self, fg_color=BG_MAIN)
        opts.pack(fill="x", padx=16, pady=(0, 8))
        
        ctk.CTkCheckBox(
            opts, text="Activar Timestamp", 
            text_color=TXT, 
            font=("", 13),
            variable=self.ts_var
        ).pack(side="left", padx=(0, 16))
        
        ctk.CTkCheckBox(
            opts, text="Activar CR/LF", 
            text_color=TXT, 
            font=("", 13),
            variable=self.cr_lf_var
        ).pack(side="left")