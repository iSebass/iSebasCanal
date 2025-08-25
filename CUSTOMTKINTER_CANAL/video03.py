import customtkinter as ctk




lista_cbo = ["Rojo", "amarillo", "verde"]

class App( ctk.CTk ):

    def __init__(self):
        super().__init__()
        self.geometry("400x600")
        self.title("iSebas APP VIDEO 03")


        self.combobox = ctk.CTkComboBox(self, values=lista_cbo, command= self.combobox_callback)
        self.combobox.set(lista_cbo[1])
        self.combobox.pack()

    def combobox_callback(self, value):
        print("Cambio Valor CBO: ", value)

if __name__=="__main__":
    app = App()
    app.mainloop()
