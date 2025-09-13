import customtkinter as ctk
from .config import *
from .components.topbar import Topbar 
from .components.sidebar import Sidebar
from .components.bottombar import Bottombar
from .pages.monitor import MonitorPage
from .pages.dashboard import DashboardPage 
from .pages.actuadores import ActuadoresPage
from .pages.iot import IoTPage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()                   

        # ===== Ventana =====
        self.title("iSebas HMI")  
        self.geometry("1000x650")            
        self.configure(fg_color=BG_MAIN)     

        # ===== Estado Serie =====
        self.baudrates = ["4800", "9600", "19200", "38400", "115200"]  
        self.ports_cache = []                       
        self.port_var = ctk.StringVar(value="")  
        self.ser = None       
        self._rx_after_id = None  

        # Variables de estado
        self.cr_lf_var = ctk.BooleanVar(value=True)
        self.ts_var = ctk.BooleanVar(value=True)

        # Componentes principales
        self.topbar = Topbar(self)
        self.topbar.pack(side="top", fill="x")

        # Body (Sidebar + Content)
        self.body = ctk.CTkFrame(self, fg_color=BG_MAIN)                 
        self.body.pack(side="top", fill="both", expand=True)             

        # Sidebar
        self.sidebar = Sidebar(self.body, self)
        self.sidebar.pack(side="left", fill="y")

        # Content area
        self.content = ctk.CTkFrame(self.body, fg_color=BG_MAIN)                  
        self.content.pack(side="left", fill="both", expand=True)                  

        # Pages
        self.pages = {
            "MonitorSerie": MonitorPage(self.content, self),
            #"Dashboard": DashboardPage(self.content),
            #"Actuadores": ActuadoresPage(self.content),
            #"IoT": IoTPage(self.content)
        }

        for p in self.pages.values():                                             
            p.place(relx=0, rely=0, relwidth=1, relheight=1)
            p.lower()

        # Bottom bar
        self.bottombar = Bottombar(self)
        self.bottombar.pack(side="bottom", fill="x")

        # Inicio
        self._scan_ports_once()                                        
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)        
        self.show_monitor()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def show_monitor(self): 
        self.sidebar.activate_button("MonitorSerie")
        self.pages["MonitorSerie"].lift()

    def show_dashboard(self):
        self.sidebar.activate_button("Dashboard") 
        self.pages["Dashboard"].lift()

    def show_actuadores(self):
        self.sidebar.activate_button("Actuadores")
        self.pages["Actuadores"].lift()

    def show_iot(self):
        self.sidebar.activate_button("IoT")
        self.pages["IoT"].lift()

    # ---- Métodos para el manejo del puerto serie ----
    def _get_ports(self):                                              
        return [p.device for p in list_ports.comports()]

    def _scan_ports_once(self):                                        
        ports = self._get_ports()
        if ports != self.ports_cache:
            self.ports_cache = ports[:]
            current = self.port_var.get()
            self.topbar.update_ports(ports)
            
            if current in ports:
                self.port_var.set(current)
            else:
                self.port_var.set(ports[0] if ports else "")
                if current and current not in ports:
                    self.bottombar.set_info(f"El puerto '{current}' ya no está disponible.")
            if not ports:
                self.bottombar.set_info("No hay puertos disponibles.")

    def _scan_ports_periodic(self):                                    
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)

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
                    self.pages["MonitorSerie"].append_text(text)
        except Exception as e:
            print(f"[RX ERROR] {e}")

        self._rx_after_id = self.after(RX_POLL_MS, self._rx_loop)

    def _on_close(self):                                               
        try:
            self._stop_rx_loop()
        finally:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.close()
            finally:
                self.destroy()

    def connect_serial(self, port, baudrate):
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
            self._start_rx_loop()
            return True, ""
        except Exception as e:
            self.ser = None
            return False, str(e)

    def disconnect_serial(self):
        self._stop_rx_loop()
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def send_serial(self, text):
        if self.ser and self.ser.is_open:
            if self.cr_lf_var.get():
                text += "\r\n"
            try:
                self.ser.write(text.encode())
                return True
            except Exception:
                return False
        return False