import customtkinter as ctk

class App( ctk.CTk ):

    def __init__(self):
        super().__init__()

        self.geometry("800x500")
        self.title("iSebas APP VIDEO 04")

        self.puertos   = ["COM1", "COM2", "COM3"]
        self.baudrates = ["4800", "9600", "19200", "38400", "115200"]

        self.topbar = ctk.CTkFrame(
            self,
            height=80,
            fg_color="#E117EF",
            corner_radius=0
        )
        self.topbar.pack(side="top", fill="x")

        self.lbl_puertos = ctk.CTkLabel(
            self.topbar,
            text="Puertos: "
        )
        self.lbl_puertos.pack(side="left", padx=30)

        #COMBO BOX PARA PUERTOS
        self.cbo_puertos = ctk.CTkComboBox(
            self.topbar,
            values = self.puertos,
            command=self.cbo_puertos_callback
        )
        self.cbo_puertos.pack(side="left", padx=30, pady=30)

        self.lbl_baudrates = ctk.CTkLabel(
            self.topbar,
            text="BAUDRATES: "
        )
        self.lbl_baudrates.pack(side="left", padx=30)

        #COMBOBOX PARA BAUDRATES
        self.cbo_baudrates = ctk.CTkComboBox(
            self.topbar,
            values = self.baudrates,
            command=self.cbo_baudrates_callback
        )
        self.cbo_baudrates.pack(side="left", padx=30, pady=30)
    
    #FUNCIONES DE ACTIVACION DEL CBO
    def cbo_puertos_callback(self, values):
        pass

    def cbo_baudrates_callback(self, values):
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()