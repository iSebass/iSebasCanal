import customtkinter as ctk

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.geometry("800x500")
        self.title("iSebas APP VIDEO 04")

        # Paleta Material Design
        self.bg_color        = "#F5F5F5"   # Fondo principal
        self.topbar_color    = "#FFFFFF"   # Panel superior
        self.text_color      = "#212121"   # Texto
        self.button_color    = "#1976D2"   # Botón principal (azul)
        self.button_hover    = "#1565C0"   # Hover azul más oscuro

        self.configure(fg_color=self.bg_color)

        self.puertos   = ["COM1", "COM2", "COM3"]
        self.baudrates = ["4800", "9600", "19200", "38400", "115200"]

        # TOPBAR
        self.topbar = ctk.CTkFrame(
            self,
            height=40,
            fg_color=self.topbar_color,
            corner_radius=0
        )
        self.topbar.pack(side="top", fill="x")

        self.lbl_puertos = ctk.CTkLabel(
            self.topbar,
            text="Puertos:",
            text_color=self.text_color
        )
        self.lbl_puertos.pack(side="left", padx=16)

        # COMBO BOX PARA PUERTOS
        self.cbo_puertos = ctk.CTkComboBox(
            self.topbar,
            values=self.puertos,
            command=self.cbo_puertos_callback,
            fg_color=self.button_color,
            text_color="white",       # Texto en blanco para contraste
            button_color=self.button_hover
        )
        self.cbo_puertos.pack(side="left", padx=16, pady=10)

        self.lbl_baudrates = ctk.CTkLabel(
            self.topbar,
            text="BAUDRATES:",
            text_color=self.text_color
        )
        self.lbl_baudrates.pack(side="left", padx=16)

        # COMBOBOX PARA BAUDRATES
        self.cbo_baudrates = ctk.CTkComboBox(
            self.topbar,
            values=self.baudrates,
            command=self.cbo_baudrates_callback,
            fg_color=self.button_color,
            text_color="white",
            button_color=self.button_hover
        )
        self.cbo_baudrates.pack(side="left", padx=16, pady=10)

        # ESTADO DE CONEXIÓN
        self.lbl_estado_conex = ctk.CTkLabel(
            self.topbar,
            text="Esperando...",
            text_color=self.text_color
        )
        self.lbl_estado_conex.pack(side="left", padx=(6, 16))

        # BOTÓN CONECTAR
        self.btn_connect = ctk.CTkButton(
            self.topbar,
            text="Conectar",
            fg_color=self.button_color,
            hover_color=self.button_hover,
            text_color="white",
            command=self.btn_connect_callback
        )
        self.btn_connect.pack(side="right", padx=16)

    # FUNCIONES DE BTN
    def btn_connect_callback(self):
        if self.btn_connect.cget("text") == "Conectar":
            self.btn_connect.configure(text="Desconectar", fg_color="#43A047", hover_color="#2E7D32") # Verde Material Design
            self.lbl_estado_conex.configure(text="Conectado OK", text_color="#43A047")
        else:
            self.btn_connect.configure(text="Conectar", fg_color=self.button_color, hover_color=self.button_hover)
            self.lbl_estado_conex.configure(text="Desconectado OK", text_color="#E53935") # Rojo error

    # FUNCIONES DE ACTIVACION DEL CBO
    def cbo_puertos_callback(self, values):
        pass

    def cbo_baudrates_callback(self, values):
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
