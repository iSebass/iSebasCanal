# HMI/router.py
from .pages.dashboard import DashboardPage
from .pages.monitor import MonitorSeriePage
from .pages.actuadores import ActuadoresPage
from .pages.iot import IoTPage
from .pages.settings import SettingsPage
from .pages.about import AboutPage  # si la tienes

class Router:
    def __init__(self, content, serial_manager, status_cb):
        self.content = content
        self.serial = serial_manager
        self.status_cb = status_cb
        self.pages = {}  # cache de instancias

    def get_or_create(self, route: str):
        if route in self.pages:
            return self.pages[route]

        if route == "dashboard":
            page = DashboardPage(self.content)
        elif route == "monitor":
            # Asegura única instancia de Dashboard y pásala al Monitor
            dash = self.get_or_create("dashboard")
            page = MonitorSeriePage(self.content, self.serial, self.status_cb, dashboard=dash)
        elif route == "actuadores":
            page = ActuadoresPage(self.content)
        elif route == "iot":
            page = IoTPage(self.content)
        elif route == "settings":
            page = SettingsPage(self.content)
        elif route == "about":
            page = AboutPage(self.content)
        else:
            # fallback
            page = DashboardPage(self.content)

        page.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.pages[route] = page
        return page

    def navigate(self, route: str):
        page = self.get_or_create(route)
        page.lift()
        return page
