import customtkinter as ctk
import pywinstyles
from serial_bridge import SerialBridge
from com0com_manager import Com0ComManager
import threading
import queue
import sys
import os
import ctypes
import tkinter.messagebox as messagebox

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyBridge - COM Port Connector & Manager")
        self.geometry("700x600")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Apply Modern Windows Style
        try:
            pywinstyles.apply_style(self, "mica")
        except:
            pass

        # Variables
        self.bridge = None
        self.is_running = False
        self.log_queue = queue.Queue()
        self.com_manager = Com0ComManager()

        # UI Components
        self.create_widgets()
        
        # Periodic check for logs
        self.after(100, self.process_logs)

    def create_widgets(self):
        # Header
        self.header = ctk.CTkLabel(self, text="PyBridge", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")

        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.tab_bridge = self.tabview.add("Puente (Relay)")
        self.tab_admin = self.tabview.add("Admin Puertos (Virtual)")

        self.setup_bridge_tab()
        self.setup_admin_tab()

    def setup_bridge_tab(self):
        self.tab_bridge.grid_columnconfigure(0, weight=1)
        self.tab_bridge.grid_rowconfigure(3, weight=1)

        # Controls Frame
        self.controls_frame = ctk.CTkFrame(self.tab_bridge)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Port A
        self.label_a = ctk.CTkLabel(self.controls_frame, text="Puerto A:")
        self.label_a.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.port_a_var = ctk.StringVar(value="Seleccionar...")
        self.combo_a = ctk.CTkComboBox(self.controls_frame, variable=self.port_a_var, values=self.get_ports())
        self.combo_a.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Port B
        self.label_b = ctk.CTkLabel(self.controls_frame, text="Puerto B:")
        self.label_b.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")
        self.port_b_var = ctk.StringVar(value="Seleccionar...")
        self.combo_b = ctk.CTkComboBox(self.controls_frame, variable=self.port_b_var, values=self.get_ports())
        self.combo_b.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        # Baudrate
        self.label_baud = ctk.CTkLabel(self.controls_frame, text="Baudios:")
        self.label_baud.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="w")
        self.baud_var = ctk.StringVar(value="9600")
        self.combo_baud = ctk.CTkComboBox(self.controls_frame, variable=self.baud_var, 
                                        values=["2400", "4800", "9600", "19200", "38400", "57600", "115200"])
        self.combo_baud.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        # Action Buttons
        self.btn_refresh = ctk.CTkButton(self.tab_bridge, text="Actualizar Lista", command=self.refresh_ports, fg_color="gray", width=120)
        self.btn_refresh.grid(row=1, column=0, padx=10, pady=5, sticky="ne")

        self.btn_action = ctk.CTkButton(self.tab_bridge, text="INICIAR PUENTE", command=self.toggle_bridge, 
                                      fg_color="#1f538d", hover_color="#14375e", height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_action.grid(row=1, column=0, padx=10, pady=5, sticky="nw")

        # Log Monitor
        self.log_text = ctk.CTkTextbox(self.tab_bridge)
        self.log_text.grid(row=3, column=0, padx=10, pady=(10, 20), sticky="nsew")
        self.log_text.configure(state="disabled")

    def setup_admin_tab(self):
        self.tab_admin.grid_columnconfigure(0, weight=1)
        
        # Admin Warning
        if not self.com_manager.is_admin():
            self.warn_frame = ctk.CTkFrame(self.tab_admin, fg_color="#4a0f0f")
            self.warn_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
            self.warn_label = ctk.CTkLabel(self.warn_frame, text="⚠ REQUIERE PERMISOS DE ADMINISTRADOR PARA CREAR PUERTOS", 
                                          text_color="white", font=ctk.CTkFont(weight="bold"))
            self.warn_label.pack(pady=10)
        
        # Create Frame
        self.create_port_frame = ctk.CTkFrame(self.tab_admin)
        self.create_port_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.create_port_frame.grid_columnconfigure((0, 1), weight=1)

        self.label_new_a = ctk.CTkLabel(self.create_port_frame, text="Puerto Virtual A (ej. COM20):")
        self.label_new_a.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_new_a = ctk.CTkEntry(self.create_port_frame, placeholder_text="COM20")
        self.entry_new_a.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.label_new_b = ctk.CTkLabel(self.create_port_frame, text="Puerto Virtual B (ej. COM21):")
        self.label_new_b.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.entry_new_b = ctk.CTkEntry(self.create_port_frame, placeholder_text="COM21")
        self.entry_new_b.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.btn_create_v = ctk.CTkButton(self.create_port_frame, text="INSTALAR NUEVO PAR", 
                                        command=self.create_virtual_pair, fg_color="#1e7b1e", hover_color="#145414")
        self.btn_create_v.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # List Frame
        self.list_frame = ctk.CTkFrame(self.tab_admin)
        self.list_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.list_label = ctk.CTkLabel(self.list_frame, text="Pares Instalados:", font=ctk.CTkFont(weight="bold"))
        self.list_label.pack(pady=5)

        self.v_ports_text = ctk.CTkTextbox(self.list_frame, height=150)
        self.v_ports_text.pack(padx=10, pady=5, fill="both")
        self.btn_list_v = ctk.CTkButton(self.list_frame, text="Refrescar Lista", command=self.refresh_v_list)
        self.btn_list_v.pack(pady=5)

        self.combo_remove_var = ctk.StringVar(value="")
        self.combo_remove_v = ctk.CTkComboBox(self.list_frame, variable=self.combo_remove_var, values=[""], state="readonly", width=300)
        self.combo_remove_v.pack(pady=5)

        self.btn_remove_v = ctk.CTkButton(self.list_frame, text="Eliminar Par Seleccionado", 
                                         command=self.remove_virtual_pair, fg_color="#a11515", hover_color="#7a0f0f")
        self.btn_remove_v.pack(pady=5)

    def get_ports(self):
        physical = SerialBridge.get_available_ports()
        
        # Include virtual ports because PySerial might miss them if they don't have the standard device class
        virtual_ports = []
        for idx, p1, p2 in self.com_manager.list_pairs():
            if p1 not in virtual_ports: virtual_ports.append(p1)
            if p2 not in virtual_ports: virtual_ports.append(p2)
            
        all_ports = physical.copy()
        for vp in virtual_ports:
            if vp not in all_ports:
                all_ports.append(vp)
        return all_ports

    def refresh_ports(self):
        ports = self.get_ports()
        self.combo_a.configure(values=ports)
        self.combo_b.configure(values=ports)
        self.log_msg("Lista de puertos físicos actualizada.")

    def log_msg(self, message):
        self.log_queue.put(message)

    def process_logs(self):
        if not self.log_queue.empty():
            self.log_text.configure(state="normal")
            msgs = []
            # Tomar máximo 50 mensajes por ciclo para no congelar la UI
            while not self.log_queue.empty() and len(msgs) < 50:
                msgs.append(self.log_queue.get())
            
            if msgs:
                self.log_text.insert("end", "".join([f"{msg}\n" for msg in msgs]))
                self.log_text.see("end")
                
            self.log_text.configure(state="disabled")
        self.after(100, self.process_logs)

    def toggle_bridge(self):
        if not self.is_running:
            port_a = self.port_a_var.get()
            port_b = self.port_b_var.get()
            baud = int(self.baud_var.get())

            if port_a == "Seleccionar..." or port_b == "Seleccionar...":
                self.log_msg("Error: Seleccione ambos puertos.")
                return

            self.bridge = SerialBridge(port_a, port_b, baud, log_callback=self.log_msg)
            success, msg = self.bridge.start()
            
            if success:
                self.is_running = True
                self.btn_action.configure(text="DETENER PUENTE", fg_color="#a11515", hover_color="#7a0f0f")
            else:
                self.log_msg(f"Error al iniciar: {msg}")
        else:
            if self.bridge: self.bridge.stop()
            self.is_running = False
            self.btn_action.configure(text="INICIAR PUENTE", fg_color="#1f538d", hover_color="#14375e")

    # Virtual Ports Functions
    def refresh_v_list(self):
        pairs = self.com_manager.list_pairs()
        self.v_ports_text.configure(state="normal")
        self.v_ports_text.delete("1.0", "end")
        combo_values = []
        if not pairs:
            self.v_ports_text.insert("end", "No hay pares virtuales instalados.\n")
            self.combo_remove_var.set("Ninguno")
            combo_values = ["Ninguno"]
        else:
            for idx, p1, p2 in pairs:
                self.v_ports_text.insert("end", f"Par {idx}: {p1} <-> {p2}\n")
                combo_values.append(f"Par {idx}: {p1} <-> {p2}")
            self.combo_remove_var.set(combo_values[0])
            
        self.combo_remove_v.configure(values=combo_values)
        self.v_ports_text.configure(state="disabled")

    def create_virtual_pair(self):
        pa = self.entry_new_a.get().strip().upper()
        pb = self.entry_new_b.get().strip().upper()
        if not pa or not pb:
            messagebox.showwarning("Faltan Datos", "Por favor, ingresa los nombres de ambos puertos (ej. COM20, COM21).")
            return
        
        # com0com can be picky about already existing ports
        success, out = self.com_manager.create_pair(pa, pb)
        if success:
            messagebox.showinfo("Éxito", f"Par {pa} <-> {pb} instalado correctamente.")
            self.refresh_v_list()
            self.refresh_ports() # Refresh the bridge dropdowns too
        else:
            messagebox.showerror("Error de Instalación", f"No se pudo instalar el par:\n\n{out}")

    def remove_virtual_pair(self):
        selection = self.combo_remove_var.get()
        if selection == "Ninguno" or not selection:
            messagebox.showinfo("INFO", "No hay pares seleccionados para eliminar.")
            return
            
        try:
            # Extract index, which is right after 'Par '
            idx_str = selection.split(":")[0].replace("Par ", "").strip()
            index = int(idx_str)
        except:
            return
            
        if messagebox.askyesno("Confirmar", f"¿Seguro que quieres eliminar el {selection}?"):
            success, out = self.com_manager.remove_pair(index)
            if success:
                messagebox.showinfo("Éxito", "Par virtual eliminado.")
                self.refresh_v_list()
                self.refresh_ports()
            else:
                messagebox.showerror("Error", f"Error al eliminar:\n\n{out}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
