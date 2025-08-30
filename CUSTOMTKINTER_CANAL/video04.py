import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("800x500")
        self.title("iSebas VIDEO 04")

        # Datos base (puedes llenarlos dinámicamente más adelante)
        self.puertos = ["COM1", "COM2", "COM3"]
        self.baudrates = ["4800", "9600", "19200", "38400", "57600", "115200"]

        # === TOP BAR / TOOLBAR ===
        self.topbar = ctk.CTkFrame(
            self, 
            height=48, 
            corner_radius=0, 
            fg_color="gray15"
        )
        self.topbar.pack(side="top", fill="x")

        # Puerto
        lbl_puerto = ctk.CTkLabel(self.topbar, text="Puerto:")
        lbl_puerto.pack(side="left", padx=(10, 6), pady=8)

        self.cbo_puerto = ctk.CTkComboBox(
            self.topbar, 
            values=self.puertos, 
            width=140,
            command=self.on_change_puerto
        )
        if self.puertos:
            self.cbo_puerto.set(self.puertos[0])
        self.cbo_puerto.pack(side="left", padx=(0, 12), pady=8)

        # Baudrate
        lbl_baud = ctk.CTkLabel(self.topbar, text="Baudrate:")
        lbl_baud.pack(side="left", padx=(0, 6), pady=8)

        self.cbo_baud = ctk.CTkComboBox(
            self.topbar, 
            values=self.baudrates, 
            width=120,
            command=self.on_change_baud
        )
        
        self.cbo_baud.set("9600")
        self.cbo_baud.pack(side="left", padx=(0, 12), pady=8)

        # Info (por ejemplo, estado)
        self.lbl_info = ctk.CTkLabel(
            self.topbar, 
            text="Desconectado", 
            text_color="gray80"
        )
        self.lbl_info.pack(side="left", padx=(0, 12), pady=8)

        # Separador flexible para empujar botones a la derecha
        spacer = ctk.CTkLabel(self.topbar, text="")
        spacer.pack(side="left", fill="x", expand=True)

        # Botones Conectar / Desconectar
        self.btn_conectar = ctk.CTkButton(
            self.topbar, 
            text="Conectar", 
            width=110,
            command=self.on_conectar
        )
        self.btn_conectar.pack(side="right", padx=(8, 10), pady=8)

        self.btn_desconectar = ctk.CTkButton(
            self.topbar, 
            text="Desconectar", 
            width=110,
            fg_color="#8b1e1e", 
            hover_color="#6b1515",
            command=self.on_desconectar
        )
        self.btn_desconectar.pack(side="right", padx=0, pady=8)

    # ==== Callbacks de ejemplo ====
    def on_change_puerto(self, value):
        print("Puerto seleccionado:", value)

    def on_change_baud(self, value):
        print("Baudrate seleccionado:", value)

    def on_conectar(self):
        self.lbl_info.configure(text="Conectando...")
        # Aquí conectas tu serial. Al finalizar:
        self.lbl_info.configure(text=f"Conectado a {self.cbo_puerto.get()} @ {self.cbo_baud.get()}")

    def on_desconectar(self):
        # Aquí cierras tu serial. Al finalizar:
        self.lbl_info.configure(text="Desconectado")

    # Método útil si luego escaneas puertos y quieres refrescar la lista:
    def set_puertos(self, lista):
        self.cbo_puerto.configure(values=lista)
        if lista:
            self.cbo_puerto.set(lista[0])

if __name__ == "__main__":
    app = App()
    app.mainloop()
