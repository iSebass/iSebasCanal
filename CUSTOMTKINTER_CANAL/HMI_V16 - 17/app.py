# ============================
# hmi/app.py
# ============================
import customtkinter as ctk
from .theme import BG_MAIN, PANEL, SCAN_INTERVAL_MS, RX_POLL_MS, setup_theme, APP_TITLE, APP_SIZE
from .services.serial_port import SerialManager
from .ui.topbar import TopBar
from .ui.sidebar import SideBar
from .router import Router


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        setup_theme()

        # ===== Ventana =====
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.configure(fg_color=BG_MAIN)

        # ===== Servicios =====
        self.serial = SerialManager()
        self._rx_after_id = None

        # ===== Topbar =====
        self.topbar = TopBar(self, self.serial, self._toggle_connect, self._set_status)
        self.topbar.pack(side="top", fill="x")

        # ===== Body =====
        body = ctk.CTkFrame(self, fg_color=BG_MAIN)
        body.pack(side="top", fill="both", expand=True)

        self.sidebar = SideBar(body, self._on_nav)
        self.sidebar.pack(side="left", fill="y")

        self.content = ctk.CTkFrame(body, fg_color=BG_MAIN)
        self.content.pack(side="left", fill="both", expand=True)

        # ===== Bottombar =====
        self.bottombar = ctk.CTkFrame(self, height=34, fg_color=PANEL, corner_radius=0)
        self.bottombar.pack(side="bottom", fill="x")
        self.lbl_status = ctk.CTkLabel(self.bottombar, text="Listo.")
        self.lbl_status.pack(expand=True)

        # ===== Router =====
        self.router = Router(self.content, self.serial, self._set_status)
        self.router.navigate("dashboard")

        # ===== Scans y eventos =====
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- Navegación ----------
    def _on_nav(self, route: str):
        page = self.router.navigate(route)
        self._set_status(f"➡️ {page.title}")

    # ---------- Estado ----------
    def _set_status(self, text: str):
        self.lbl_status.configure(text=text)

    # ---------- Scan de puertos ----------
    def _scan_ports_once(self):
        ports = self.serial.list_ports()
        self.topbar.update_ports(ports)

    def _scan_ports_periodic(self):
        self._scan_ports_once()
        self.after(SCAN_INTERVAL_MS, self._scan_ports_periodic)

    # ---------- Conexión ----------
    def _toggle_connect(self):
        if self.serial.is_open():
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        port, baud = self.topbar.get_selected_port_and_baud()
        if not port or not baud:
            self._set_status("⚠️ Selecciona puerto y baudrate válido.")
            return
        if not self.serial.connect(port, baud):
            self._set_status(f"❌ Error al abrir {port}.")
            return
        self.topbar.set_connected(True)
        self._set_status(f"✅ Conectado a {port} @ {baud} bps")
        self._start_rx_loop()

    def _disconnect(self):
        self._stop_rx_loop()
        self.serial.close()
        self.topbar.set_connected(False)
        self._set_status("🔌 Desconectado")

    # ---------- RX Loop (sólo aplica si la página monitor está presente) ----------
    def _rx_loop(self):
        page = self.router.pages.get("monitor")
        if page is not None:
            try:
                page.poll_rx_and_render(stamped=True)
            except Exception:
                pass
        self._rx_after_id = self.after(RX_POLL_MS, self._rx_loop)

    def _start_rx_loop(self):
        if not getattr(self, "_rx_after_id", None):
            self._rx_loop()

    def _stop_rx_loop(self):
        if getattr(self, "_rx_after_id", None):
            try:
                self.after_cancel(self._rx_after_id)
            except Exception:
                pass
            self._rx_after_id = None

    # ---------- Cierre ----------
    def _on_close(self):
        try:
            self._stop_rx_loop()
        finally:
            try:
                self.serial.close()
            finally:
                self.destroy()