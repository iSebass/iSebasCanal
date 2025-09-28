# ============================
# hmi/pages/actuadores.py
# ============================
import customtkinter as ctk
from .base import BasePage
from ..theme import PANEL, BG_MAIN, TXT

# ====== Tokens locales de tarjeta ======
CARD_BG   = PANEL
RADIUS    = 14
PAD       = 12

# ====== Paleta GPIO ON/OFF ======
GPIO_ON_BG     = "#16A34A"   # verde vivo
GPIO_ON_HOVER  = "#22C55E"
GPIO_ON_TXT    = "#FFFFFF"

GPIO_OFF_BG    = "#1F2937"   # gris oscuro
GPIO_OFF_HOVER = "#374151"
GPIO_OFF_TXT   = "#E5E7EB"


def make_card(parent, title: str, subtitle: str | None = None):
    """
    Crea una 'tarjeta' estilo dashboard con header y body.
    Retorna (card, body) para que el caller ponga su contenido en body.
    """
    card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=RADIUS)
    card.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(card, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=PAD, pady=(PAD, 4))
    header.grid_columnconfigure(0, weight=1)

    title_lbl = ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=16, weight="bold"))
    title_lbl.grid(row=0, column=0, sticky="w")

    if subtitle:
        sub_lbl = ctk.CTkLabel(header, text=subtitle, text_color="#6B7280", font=ctk.CTkFont(size=12))
        sub_lbl.grid(row=1, column=0, sticky="w")

    body = ctk.CTkFrame(card, fg_color="transparent")
    body.grid(row=1, column=0, sticky="nsew", padx=PAD, pady=(0, PAD))
    card.grid_rowconfigure(1, weight=1)
    return card, body


# ====== Botón Toggle con colores vivos (usa constantes) ======
class ToggleButton(ctk.CTkButton):
    """
    Botón tipo toggle: muestra ON/OFF y cambia colores.
    Llama a `command(state:int)` con 1 (ON) o 0 (OFF).
    """
    def __init__(self, master, text_on="ON", text_off="OFF", state=False, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self._text_on = text_on
        self._text_off = text_off
        self._state = bool(state)
        self._user_cmd = command

        self.configure(corner_radius=10, height=36)
        self._apply_style()
        self.configure(command=self._toggle)

    def _apply_style(self):
        if self._state:
            self.configure(
                text=self._text_on,
                fg_color=GPIO_ON_BG,
                hover_color=GPIO_ON_HOVER,
                text_color=GPIO_ON_TXT,
            )
        else:
            self.configure(
                text=self._text_off,
                fg_color=GPIO_OFF_BG,
                hover_color=GPIO_OFF_HOVER,
                text_color=GPIO_OFF_TXT,
            )

    def _toggle(self):
        self._state = not self._state
        self._apply_style()
        if self._user_cmd:
            self._user_cmd(1 if self._state else 0)

    def set_state(self, value: int | bool):
        self._state = bool(value)
        self._apply_style()

    def get_state(self) -> int:
        return 1 if self._state else 0


# ============================
# Tarjeta: GPIO (con botones ON/OFF coloridos)
# ============================
class GPIOCard(ctk.CTkFrame):
    def __init__(self, master, on_change=None):
        super().__init__(master, fg_color="transparent")
        self.on_change = on_change

        card, body = make_card(self, "CARD GPIO", "Botones ON/OFF")
        card.pack(fill="x")

        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.grid(row=0, column=0, sticky="ew")
        for c in (0, 1, 2, 3, 4,5):
            grid.grid_columnconfigure(c, weight=1 if c in (1, 3,5) else 0)

        self._btns = []
        labels = ["LED 1", "LED 2", "LED 3"]
        for i, name in enumerate(labels):
            lbl = ctk.CTkLabel(grid, text=name, font=ctk.CTkFont(size=14, weight="bold"))
            lbl.grid(row=0, column=i*2, sticky="e", padx=(0, 6), pady=6)

            btn = ToggleButton(
                grid,
                text_on="ON",
                text_off="OFF",
                state=False,
                command=lambda val, idx=i: self._emit(idx + 1, val),
                width=90,
            )
            btn.grid(row=0, column=i*2 + 1, sticky="w", padx=(0, 10), pady=6)
            self._btns.append(btn)

    def _emit(self, pin_idx: int, value: int):
        if self.on_change:
            self.on_change(pin_idx, value)

    def set_state(self, idx: int, value: int):
        if 1 <= idx <= len(self._btns):
            self._btns[idx - 1].set_state(value)

    def get_state(self, idx: int) -> int:
        if 1 <= idx <= len(self._btns):
            return self._btns[idx - 1].get_state()
        return 0


# ============================
# Tarjeta: PWM (2 canales)
# ============================
class PWMCard(ctk.CTkFrame):
    def __init__(self, master, on_change=None):
        super().__init__(master, fg_color="transparent")
        self.on_change = on_change

        card, body = make_card(self, "PWM", "Dos canales (0–255)")
        card.pack(fill="x", pady=(8, 0))

        row = 0
        self.lbl1 = ctk.CTkLabel(body, text="PWM1: 0")
        self.lbl1.grid(row=row, column=0, sticky="w")
        self.sld1 = ctk.CTkSlider(body, from_=0, to=255, command=self._on_pwm1)
        self.sld1.grid(row=row, column=1, sticky="ew", padx=8)
        body.grid_columnconfigure(1, weight=1)

        row += 1
        self.lbl2 = ctk.CTkLabel(body, text="PWM2: 0")
        self.lbl2.grid(row=row, column=0, sticky="w", pady=(8, 0))
        self.sld2 = ctk.CTkSlider(body, from_=0, to=255, command=self._on_pwm2)
        self.sld2.grid(row=row, column=1, sticky="ew", padx=8, pady=(8, 0))

    def _on_pwm1(self, v):
        v = int(float(v))
        self.lbl1.configure(text=f"PWM1: {v}")
        if self.on_change:
            self.on_change(1, v)

    def _on_pwm2(self, v):
        v = int(float(v))
        self.lbl2.configure(text=f"PWM2: {v}")
        if self.on_change:
            self.on_change(2, v)

    def set_value(self, ch: int, v: int):
        if ch == 1:
            self.sld1.set(v); self.lbl1.configure(text=f"PWM1: {int(v)}")
        elif ch == 2:
            self.sld2.set(v); self.lbl2.configure(text=f"PWM2: {int(v)}")


# ============================
# Tarjeta: Servos (2 canales)
# ============================
class ServosCard(ctk.CTkFrame):
    def __init__(self, master, on_change=None):
        super().__init__(master, fg_color="transparent")
        self.on_change = on_change

        card, body = make_card(self, "Servos", "Dos servos (0–180)")
        card.pack(fill="x", pady=(8, 0))

        row = 0
        self.s1_lbl = ctk.CTkLabel(body, text="Servo A: 0°")
        self.s1_lbl.grid(row=row, column=0, sticky="w")
        self.s1 = ctk.CTkSlider(body, from_=0, to=180, command=self._on_s1)
        self.s1.grid(row=row, column=1, sticky="ew", padx=8)
        body.grid_columnconfigure(1, weight=1)

        row += 1
        self.s2_lbl = ctk.CTkLabel(body, text="Servo B: 0°")
        self.s2_lbl.grid(row=row, column=0, sticky="w", pady=(8, 0))
        self.s2 = ctk.CTkSlider(body, from_=0, to=180, command=self._on_s2)
        self.s2.grid(row=row, column=1, sticky="ew", padx=8, pady=(8, 0))

        btns = ctk.CTkFrame(body, fg_color="transparent")
        btns.grid(row=row + 1, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ctk.CTkButton(btns, text="Centrar A (90°)", command=lambda: self.set_angle(1, 90)).grid(row=0, column=0, padx=6)
        ctk.CTkButton(btns, text="Centrar B (90°)", command=lambda: self.set_angle(2, 90)).grid(row=0, column=1, padx=6)

    def _on_s1(self, v):
        v = int(float(v))
        self.s1_lbl.configure(text=f"Servo A: {v}°")
        if self.on_change:
            self.on_change(1, v)

    def _on_s2(self, v):
        v = int(float(v))
        self.s2_lbl.configure(text=f"Servo B: {v}°")
        if self.on_change:
            self.on_change(2, v)

    def set_angle(self, servo: int, angle: int):
        angle = int(angle)
        if servo == 1:
            self.s1.set(angle); self.s1_lbl.configure(text=f"Servo A: {angle}°")
        elif servo == 2:
            self.s2.set(angle); self.s2_lbl.configure(text=f"Servo B: {angle}°")


# ============================
# Página Actuadores (layout)
# ============================
class ActuadoresPage(BasePage):
    title = "Actuadores"
    subtitle = "Control (solo UI) • Plantilla modular"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        wrap = ctk.CTkFrame(self, fg_color=BG_MAIN)
        wrap.pack(fill="both", expand=True, padx=16, pady=16)
        wrap.grid_columnconfigure(0, weight=1)

        self.gpio = GPIOCard(wrap, on_change=self._gpio_changed)
        self.gpio.pack(fill="x")

        self.pwm = PWMCard(wrap, on_change=self._pwm_changed)
        self.pwm.pack(fill="x", pady=(8, 0))

        self.servos = ServosCard(wrap, on_change=self._servo_changed)
        self.servos.pack(fill="x", pady=(8, 0))

    # --- dentro de ActuadoresPage ---

    def _send(self, obj: dict):
        """Sube hasta App y usa su helper de envío."""
        app = self.winfo_toplevel()
        if hasattr(app, "send_json"):
            app.send_json(obj)

    def _gpio_changed(self, pin_idx: int, value: int):
        print(f"[UI] GPIO D{pin_idx} => {value}")
        self._send({"cmd": "digital", "ch": pin_idx, "value": int(value)})

    def _pwm_changed(self, ch: int, value: int):
        print(f"[UI] PWM{ch} => {value}")
        self._send({"cmd": "pwm", "ch": ch, "value": int(value)})

    def _servo_changed(self, servo: int, angle: int):
        print(f"[UI] SERVO{servo} => {angle}°")
        self._send({"cmd": "servo", "id": servo, "angle": int(angle)})
