# -*- coding: utf-8 -*-
# video11.py

import customtkinter as ctk                 
import serial                               
import serial.tools.list_ports as list_ports

# ===== Paleta Material Light Modern =====
BG_MAIN   = "#F9FAFB"   # fondo principal 
PANEL     = "#E5E7EB"   # frames/paneles  
TXT       = "#111827"   # texto base      
ACCENT    = "#2563EB"   # botón primario  
ACCENT_H  = "#1D4ED8"   # hover           
OK_COLOR  = "#059669"   # verde éxito     
ERR_COLOR = "#DC2626"   # rojo error      

SCAN_INTERVAL_MS = 1000  # cada 1 s       
RX_POLL_MS       = 50    # RX no bloqueant

class App(ctk.CTk):
    def __init__(self):
        super().__init__()                   

        # ===== Ventana =====
        self.title("iSebas HMI - Video 11 (Maquetado + Navegación)")  
        self.geometry("1000x650")            
        self.configure(fg_color=BG_MAIN)     

        # ===== Estado Serie =====
        self.baudrates   = ["4800", "9600", "19200", "38400", "115200"]  
        self.ports_cache = []                       
        self.port_var    = ctk.StringVar(value="")  
        self.ser: serial.Serial | None = None       
        self._rx_after_id = None                    

        # =================== TOP BAR ===================  (SIN CAMBIOS)
        self.topbar = ctk.CTkFrame(self, height=56, fg_color=PANEL, corner_radius=0)   
        self.topbar.pack(side="top", fill="x")                                         

        self.lbl_puertos = ctk.CTkLabel(self.topbar, text="Puerto:", text_color=TXT)   
        self.lbl_puertos.pack(side="left", padx=(16,6), pady=10)                       

        self.cbo_puertos = ctk.CTkComboBox(                                            
            self.topbar, values=[], width=140, variable=self.port_var,
            command=self.on_port_changed
        )
        self.cbo_puertos.set("")                                                       
        self.cbo_puertos.pack(side="left", padx=(0,16), pady=10)                       

        self.lbl_baudrates = ctk.CTkLabel(self.topbar, text="Baudios:", text_color=TXT)
        self.lbl_baudrates.pack(side="left", padx=(0,6), pady=10)                      

        self.cbo_baudrates = ctk.CTkComboBox(                                          
            self.topbar, values=self.baudrates, width=120, command=self.on_baud_changed
        )
        self.cbo_baudrates.set("9600")                                                 
        self.cbo_baudrates.pack(side="left", padx=(0,16), pady=10)                     

        self.lbl_estado = ctk.CTkLabel(self.topbar, text="Desconectado", text_color="gray")  
        self.lbl_estado.pack(side="left", padx=(0,16), pady=10)                               

        self.topbar_spacer = ctk.CTkLabel(self.topbar, text="", fg_color=PANEL)        
        self.topbar_spacer.pack(side="left", fill="x", expand=True)                    

        self.btn_connect = ctk.CTkButton(                                              
            self.topbar, text="Conectar", width=120,
            fg_color=ACCENT, hover_color=ACCENT_H, text_color="white",
            command=self._toggle_connect
        )
        self.btn_connect.pack(side="right", padx=(8,12), pady=10)                      

        # ============== BODY (Sidebar + Content) ============== 
        # (ANTES en tu video 10 solo había un label “Contenido principal”;
        # ahora montamos navegación completa con páginas)
        self.body = ctk.CTkFrame(self, fg_color=BG_MAIN)                 
        self.body.pack(side="top", fill="both", expand=True)             

        # Sidebar izquierda con botones de navegación
        self.sidebar = ctk.CTkFrame(self.body, width=210, fg_color=PANEL, corner_radius=0)  
        self.sidebar.pack(side="left", fill="y")                                            

        self.lbl_menu = ctk.CTkLabel(self.sidebar, text="MENÚ", text_color=TXT, font=("",14,"bold"))  
        self.lbl_menu.pack(pady=(14,6))                                                               

        self.nav_buttons = {}                                                     
        self._add_nav_button("MonitorSerie", self.show_monitor)                   
        self._add_nav_button("Dashboard",    self.show_dashboard)                 
        self._add_nav_button("Actuadores",   self.show_actuadores)                
        self._add_nav_button("IoT",          self.show_iot)                       

        # Área central (contenedor de páginas)
        self.content = ctk.CTkFrame(self.body, fg_color=BG_MAIN)                  
        self.content.pack(side="left", fill="both", expand=True)                  

        # Páginas “apiladas” (solo mostramos una con lift/lower)
        self.pages = {                                                            
            "MonitorSerie": self._make_page("Monitor Serie"),
            "Dashboard":    self._make_page("Dashboard"),
            "Actuadores":   self._make_page("Actuadores"),
            "IoT":          self._make_page("IoT"),
        }
        for p in self.pages.values():                                             
            p.place(relx=0, rely=0, relwidth=1, relheight=1)
            p.lower()

        # =================== BOTTOM BAR (Label centrado) ===================
        self.bottombar = ctk.CTkFrame(self, height=34, fg_color=PANEL, corner_radius=0)  
        self.bottombar.pack(side="bottom", fill="x")                                     

        self.lbl_info_bottombar = ctk.CTkLabel(self.bottombar, text="Listo.", text_color=TXT)  
        self.lbl_info_bottombar.pack(expand=True)                                               

        # ---- Primer escaneo + refresco periódico ----
        self._scan_ports_once()                                        
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)        

        # Página por defecto (resalta botón y trae al frente el frame)
        self.show_monitor()                                            

        self.protocol("WM_DELETE_WINDOW", self._on_close)              

    # ---------------- Navegación (NUEVO) ----------------
    def _add_nav_button(self, name, cmd):                              
        btn = ctk.CTkButton(
            self.sidebar, text=name, width=180,
            fg_color="#374151", hover_color="#1F2937", text_color="white",
            command=lambda n=name, c=cmd: self._on_nav(n, c)
        )
        btn.pack(padx=16, pady=6)
        self.nav_buttons[name] = btn

    def _on_nav(self, name, cmd):                                      
        for n, b in self.nav_buttons.items():
            if n == name:
                b.configure(fg_color=ACCENT, hover_color=ACCENT_H)
            else:
                b.configure(fg_color="#374151", hover_color="#1F2937")
        cmd()

    def _make_page(self, text):                                        
        frame = ctk.CTkFrame(self.content, fg_color=BG_MAIN)
        ctk.CTkLabel(frame, text=text, text_color=TXT, font=("",16,"bold")).pack(padx=12, pady=12, anchor="w")
        ctk.CTkLabel(frame, text="(Placeholder — se implementará en próximos videos)", text_color="#4B5563").pack(padx=12, anchor="w")
        return frame

    def _show_page(self, key):                                         
        for k, p in self.pages.items():
            if k == key: p.lift()
            else: p.lower()

    def show_monitor(self):   self._on_nav("MonitorSerie", lambda: self._show_page("MonitorSerie"))  
    def show_dashboard(self): self._on_nav("Dashboard",    lambda: self._show_page("Dashboard"))     
    def show_actuadores(self):self._on_nav("Actuadores",   lambda: self._show_page("Actuadores"))    
    def show_iot(self):       self._on_nav("IoT",          lambda: self._show_page("IoT"))           

    # ---------------- RX no bloqueante (MISMO QUE VIDEO 10) ----------------
    def _start_rx_loop(self):                                          
        if self._rx_after_id is None:
            self._rx_loop()

    def _stop_rx_loop(self):                                           
        if self._rx_after_id is not None:
            try:
                self.after_cancel(self._rx_after_id)
            except Exception:
                pass
            self._rx_after_id = None

    def _rx_loop(self):                                                
        try:
            if self.ser and self.ser.is_open:
                n = self.ser.in_waiting
                if n:
                    data = self.ser.read(n)
                    text = data.decode("utf-8", errors="replace")
                    print(text, end="")  # por ahora imprime en la consola de Python
        except Exception as e:
            print(f"[RX ERROR] {e}")

        self._rx_after_id = self.after(RX_POLL_MS, self._rx_loop)

    # ---------------- Cierre ordenado (MISMO QUE VIDEO 10) ----------------
    def _on_close(self):                                               
        try:
            self._stop_rx_loop()
        finally:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.close()
            finally:
                self.destroy()

    # ---------------- Escaneo de puertos (MISMO QUE VIDEO 10) ----------------
    def _get_ports(self):                                              
        return [p.device for p in list_ports.comports()]

    def _scan_ports_once(self):                                        
        ports = self._get_ports()
        if ports != self.ports_cache:
            self.ports_cache = ports[:]
            current = self.port_var.get()
            self.cbo_puertos.configure(values=ports)

            if current in ports:
                self.port_var.set(current)
            else:
                self.port_var.set(ports[0] if ports else "")
                if current and current not in ports:
                    self.lbl_info_bottombar.configure(text=f"El puerto '{current}' ya no está disponible.")
            if not ports:
                self.lbl_info_bottombar.configure(text="No hay puertos disponibles.")

    def _scan_ports_periodic(self):                                    
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)

    # ---------------- Callbacks UI (MISMO QUE VIDEO 10) ----------------
    def on_port_changed(self, value: str):                             # [VIDEO 10]
        self.lbl_info_bottombar.configure(text=f"Puerto seleccionado: {value}")

    def on_baud_changed(self, value: str):                             
        self.lbl_info_bottombar.configure(text=f"Baudrate seleccionado: {value}")

    # ---------------- Conexión / Desconexión (MISMO QUE VIDEO 10) ----------------
    def _toggle_connect(self):                                         
        if self.ser and self.ser.is_open:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):                                                
        port = self.port_var.get().strip()
        try:
            baud = int(self.cbo_baudrates.get())
        except ValueError:
            self.lbl_info_bottombar.configure(text="⚠️ Baudrate inválido.")
            return

        if not port:
            self.lbl_info_bottombar.configure(text="⚠️ Selecciona un puerto.")
            return

        try:
            self.ser = serial.Serial(port=port, baudrate=baud, timeout=0.1)
        except Exception as e:
            self.lbl_info_bottombar.configure(text=f"❌ Error al abrir {port}: {e}")
            self.ser = None
            return

        self.lbl_estado.configure(text=f"Conectado", text_color=OK_COLOR)
        self.btn_connect.configure(text="Desconectar", fg_color=ERR_COLOR, hover_color="#991B1B")
        self.cbo_puertos.configure(state="disabled")
        self.cbo_baudrates.configure(state="disabled")
        self.lbl_info_bottombar.configure(text=f"✅ Conectado a {port} @ {baud} bps")

        self._start_rx_loop()

    def _disconnect(self):                                             
        self._stop_rx_loop()

        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

        self.lbl_estado.configure(text="Desconectado", text_color="gray")
        self.btn_connect.configure(text="Conectar", fg_color=ACCENT, hover_color=ACCENT_H)
        self.cbo_puertos.configure(state="normal")
        self.cbo_baudrates.configure(state="normal")
        self.lbl_info_bottombar.configure(text="🔌 Desconectado")


if __name__ == "__main__":                     
    ctk.set_appearance_mode("light")           
    app = App()                                
    app.mainloop()                             
