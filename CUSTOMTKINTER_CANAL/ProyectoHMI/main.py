import customtkinter as ctk
from src.app import App

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = App()
    app.mainloop()