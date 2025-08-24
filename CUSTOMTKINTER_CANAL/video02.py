import customtkinter


def call_back_btn():
    print("Presionaste el boton")


app = customtkinter.CTk()

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

app.geometry("600x400")
app.title("iSebas APP")

button = customtkinter.CTkButton(app, text="Press Me", command=call_back_btn)
button.grid( row=0, column=0,  padx= 10, pady=(40,0) )

button2= customtkinter.CTkButton(app, text="Press Me", command=call_back_btn)
button2.grid( row=0, column=1, padx= 10, pady=(40,0) )

button3 = customtkinter.CTkButton(app, text="Press Me", command=call_back_btn)
button3.grid( row=0, column=2, padx= 10, pady=(40,0) )

button4= customtkinter.CTkButton(app, text="Press Me", command=call_back_btn)
button4.grid( row=1, column=0,padx= 10, pady=(40,0) )

button5= customtkinter.CTkButton(app, text="Press Me", command=call_back_btn)
button5.grid( row=1, column=1,padx= 10, pady=(40,0) )

button6= customtkinter.CTkButton(app, text="Press Me", command=call_back_btn)
button6.grid( row=1, column=2,padx= 10, pady=(40,0) )

app.mainloop()