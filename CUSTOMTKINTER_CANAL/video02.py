import customtkinter as ctk

def call_back_btn():
    print("Presionaste el boton")

def call_back_btn1():
    print("Presionaste el boton")

app = ctk.CTk()

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("dark-blue") 

app.title("iSebas APP")
app.geometry("600x400")

button = ctk.CTkButton(app, text="Press Me", command=call_back_btn)
button.grid( row=0, column =0,  padx=20,  pady=20,sticky="ew")

button1 = ctk.CTkButton(app, text="Press Me", command=call_back_btn1)
button1.grid( row=0, column =1, padx=20,  pady=20)

label1 = ctk.CTkLabel(app, text="TEXTO LBL", fg_color="transparent")
label1.grid(row=0, column =2, padx=20,  pady=20)

label2 = ctk.CTkLabel(app, text="TEXTO LBL", fg_color="transparent")
label2.grid(row=1, column =0, padx=20,  pady=20)

label3 = ctk.CTkLabel(app, text="TEXTO LBL", fg_color="transparent")
label3.grid(row=1, column =1, padx=20,  pady=20)

label4 = ctk.CTkLabel(app, text="TEXTO LBL", fg_color="transparent")
label4.grid(row=1, column =2, padx=20,  pady=20)

label5 = ctk.CTkLabel(app, text="TEXTO LBL", fg_color="transparent")
label5.grid(row=2, column =0, padx=20,  pady=20)

label6 = ctk.CTkLabel(app, text="TEXTO LBL", fg_color="transparent")
label6.grid(row=2, column =1, padx=20,  pady=20)

app.mainloop()