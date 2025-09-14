# HMI/pages/dashboard.py
import customtkinter as ctk
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .base import BasePage
from ..theme import BG_MAIN, TXT, KPI_TEMP, KPI_HUM, KPI_VOLT

RADIUS = 14
PAD    = 10
HIST_MAX = 200  # cantidad de muestras a retener

# ---------------- ChartsPanel (compacto, limpio) ----------------
class ChartsPanel(ctk.CTkFrame):
    """Panel con 3 gráficas minimalistas (Temp/Hum/Volt). Puede ocultarse sin romper layout."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#FFFFFF", corner_radius=14, **kwargs)

        self.fig = Figure(figsize=(7.5, 2.2), dpi=110)
        self.ax_t = self.fig.add_subplot(131)  # Temperatura
        self.ax_h = self.fig.add_subplot(132)  # Humedad
        self.ax_v = self.fig.add_subplot(133)  # Voltaje

        for ax, title, yl in [
            (self.ax_t, "Temperatura", "°C"),
            (self.ax_h, "Humedad", "%"),
            (self.ax_v, "Voltaje", "V"),
        ]:
            ax.set_title(title, fontsize=10, pad=6)
            ax.set_xlabel("muestras", fontsize=9)
            ax.set_ylabel(yl, fontsize=9)
            ax.grid(True, linewidth=0.5, alpha=0.35)
            ax.tick_params(labelsize=8)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        (self.l_t,) = self.ax_t.plot([], [], linewidth=1.8)
        (self.l_h,) = self.ax_h.plot([], [], linewidth=1.8)
        (self.l_v,) = self.ax_v.plot([], [], linewidth=1.8)

        self.x = deque(maxlen=HIST_MAX)
        self.yt = deque(maxlen=HIST_MAX)
        self.yh = deque(maxlen=HIST_MAX)
        self.yv = deque(maxlen=HIST_MAX)
        self._idx = 0

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=PAD, pady=PAD)

    def append(self, t=None, h=None, v=None):
        """Agrega una muestra (cualquiera de las tres)."""
        self.x.append(self._idx); self._idx += 1
        # Relleno para que todas las curvas tengan mismo largo
        last_t = self.yt[-1] if self.yt else None
        last_h = self.yh[-1] if self.yh else None
        last_v = self.yv[-1] if self.yv else None
        self.yt.append(float(t) if t is not None else (last_t if last_t is not None else 0.0))
        self.yh.append(float(h) if h is not None else (last_h if last_h is not None else 0.0))
        self.yv.append(float(v) if v is not None else (last_v if last_v is not None else 0.0))
        self._redraw()

    def _redraw(self):
        xs = list(self.x)
        self.l_t.set_data(xs, list(self.yt))
        self.l_h.set_data(xs, list(self.yh))
        self.l_v.set_data(xs, list(self.yv))

        for ax, ys in [(self.ax_t, self.yt), (self.ax_h, self.yh), (self.ax_v, self.yv)]:
            if xs:
                ax.set_xlim(xs[0], xs[-1] if xs[-1] != xs[0] else xs[0] + 1)
                ymin, ymax = min(ys) if ys else 0, max(ys) if ys else 1
                if ymin == ymax:
                    ymin -= 0.5; ymax += 0.5
                pad = (ymax - ymin) * 0.2
                ax.set_ylim(ymin - pad, ymax + pad)

        self.canvas.draw_idle()


# ---------------- KPI Cards (tus tarjetas) ----------------
class IconKPICard(ctk.CTkFrame):
    def __init__(self, master, title: str, icon: str, accent: str,
                 value_var: ctk.StringVar, unit: str = "", **kwargs):
        super().__init__(master, fg_color="#FFFFFF", corner_radius=RADIUS, height=110, **kwargs)
        header = ctk.CTkFrame(self, fg_color=accent, corner_radius=RADIUS, height=32)
        header.pack(fill="x", padx=PAD, pady=(PAD, 6))
        header.pack_propagate(False)
        ctk.CTkLabel(header, text=icon, font=("Segoe UI Emoji", 16), text_color="white")\
            .pack(side="left", padx=(8, 6))
        ctk.CTkLabel(header, text=title, font=("", 12, "bold"), text_color="white")\
            .pack(side="left")

        ctk.CTkLabel(self, textvariable=value_var, text_color=TXT, font=("", 20, "bold"))\
            .pack(pady=(0, 2))
        if unit:
            ctk.CTkLabel(self, text=unit, text_color=TXT, font=("", 10)).pack()


class DashboardPage(BasePage):
    title = "Dashboard"
    subtitle = "KPIs de Humedad, Temperatura y Voltaje"

    def __init__(self, master, show_charts=True, **kwargs):
        super().__init__(master, **kwargs)

        # Vars
        self.temp_var = ctk.StringVar(value="--")
        self.hum_var  = ctk.StringVar(value="--")
        self.volt_var = ctk.StringVar(value="--")

        root = ctk.CTkFrame(self, fg_color=BG_MAIN)
        root.pack(fill="both", expand=True, padx=16, pady=16)
        # fila KPIs
        row1 = ctk.CTkFrame(root, fg_color=BG_MAIN)
        row1.pack(fill="x")
        row1.grid_columnconfigure((0, 1, 2), weight=1, uniform="kpi")

        self.kpi_temp = IconKPICard(row1, "Temperatura", "🌡️", KPI_TEMP, self.temp_var, "°C")
        self.kpi_hum  = IconKPICard(row1, "Humedad", "💧",    KPI_HUM,  self.hum_var,  "%")
        self.kpi_volt = IconKPICard(row1, "Voltaje", "🔋",    KPI_VOLT, self.volt_var, "V")
        self.kpi_temp.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.kpi_hum.grid( row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.kpi_volt.grid(row=0, column=2, sticky="nsew", padx=8, pady=8)

        # fila Gráficas (opcional)
        self.charts_panel = None
        if show_charts:
            self.charts_panel = ChartsPanel(root)
            self.charts_panel.pack(fill="both", expand=True, padx=8, pady=(4, 0))

    # ------- API pública que ya usas -------
    def set_temp(self, v): self.temp_var.set(self._fmt(v))
    def set_hum(self, v):  self.hum_var.set(self._fmt(v))
    def set_volt(self, v): self.volt_var.set(self._fmt(v))

    def set_values(self, humedad=None, temperatura=None, voltaje=None):
        if humedad is not None:     self.set_hum(humedad)
        if temperatura is not None: self.set_temp(temperatura)
        if voltaje is not None:     self.set_volt(voltaje)
        # si hay charts y vino algo, agrega una muestra
        if self.charts_panel and any(x is not None for x in (temperatura, humedad, voltaje)):
            self.charts_panel.append(t=temperatura, h=humedad, v=voltaje)

    @staticmethod
    def _fmt(v):
        try:   return f"{float(v):.2f}"
        except: return str(v)
