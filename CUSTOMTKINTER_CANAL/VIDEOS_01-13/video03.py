import customtkinter as ctk

lista_cbo = ["Rojo", "amarillo", "verde"]


class App( ctk.CTk ):

    def __init__(self):
        super().__init__()
        self.geometry("400x600")
        self.title("iSebas APP VIDEO 03")

        self.baudrates = ["4800", "9600", "19200", "38400", "115200"]

        self.comboboxPuertos = ctk.CTkComboBox(
            self, 
            values=self.baudrates, 
            command= self.comboboxPuertos_callback
        )

        self.comboboxPuertos.set(self.baudrates[1])
        self.comboboxPuertos.grid(row=0, column=0)

        self.lblPuertos = ctk.CTkLabel(
            self, 
            text="Puerto COM", 
            fg_color="transparent"
        )
        self.lblPuertos.grid(row=0, column=1)
        
        
        


        self.combobox = ctk.CTkComboBox(
            self, 
            values=lista_cbo, 
            command= self.combobox_callback
        )
        self.combobox.set(lista_cbo[1])
        self.combobox.grid(row=1, column=0)
    
    def comboboxPuertos_callback(self, values):
        print(values)

    def combobox_callback(self, value):
        print("Cambio Valor CBO: ", value)

if __name__=="__main__":
    app = App()
    app.mainloop()
