# ============================
# hmi/router.py
# ============================
from .pages.dashboard import DashboardPage
from .pages.monitor import MonitorSeriePage
from .pages.actuadores import ActuadoresPage
from .pages.iot import IoTPage
from .pages.settings import SettingsPage
from .pages.about import AboutPage




class Router:
    def __init__(self, content_frame, serial_manager, status_cb):
        self.content = content_frame
        self.serial = serial_manager
        self.status_cb = status_cb
        self.pages = {}

    def get_or_create(self, route: str):
        if route in self.pages:
            return self.pages[route]
        # creación perezosa
        if route == "dashboard":
            page = DashboardPage(self.content)
        elif route == "monitor":
            page = MonitorSeriePage(self.content, self.serial, self.status_cb)
        elif route == "actuadores":
            page = ActuadoresPage(self.content)
        elif route == "iot":
            page = IoTPage(self.content)
        elif route == "settings":
            page = SettingsPage(self.content)
        elif route == "about":
            page = AboutPage(self.content)
        else:
            page = DashboardPage(self.content)
        page.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.pages[route] = page
        return page

    def navigate(self, route: str):
        page = self.get_or_create(route)
        page.lift()
        return page