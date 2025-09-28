# ============================
# hmi/services/serial_port.py
# ============================
from typing import Optional
import serial
import serial.tools.list_ports as list_ports


class SerialManager:
    """Capa delgada sobre pyserial para aislar la UI de detalles del puerto."""

    def __init__(self):
        self.ser: Optional[serial.Serial] = None

    # ---------- Descubrimiento ----------
    @staticmethod
    def list_ports() -> list[str]:
        return [p.device for p in list_ports.comports()]

    # ---------- Conexión ----------
    def connect(self, port: str, baudrate: int, timeout: float = 0.1) -> bool:
        self.close()
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            return True
        except Exception:
            self.ser = None
            return False

    def is_open(self) -> bool:
        return bool(self.ser and self.ser.is_open)

    def close(self):
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None

    # ---------- IO ----------
    def write_line(self, data: str, crlf: bool) -> bool:
        if not self.is_open():
            return False
        payload = (data + ("\r\n" if crlf else "")).encode("utf-8", errors="ignore")
        try:
            self.ser.write(payload)
            return True
        except Exception:
            return False

    def read_available_text(self) -> str:
        """Lee todo lo disponible sin bloquear y lo devuelve como texto."""
        if not self.is_open():
            return ""
        try:
            n = self.ser.in_waiting
            if n:
                data = self.ser.read(n)
                return data.decode("utf-8", errors="replace")
        except Exception:
            return ""
        return ""

    def write_text(self, text: str) -> bool:
        """Escribe texto UTF-8 al puerto. Retorna True si se envió."""
        if not self.is_open():
            return False
        try:
            if not text.endswith("\n"):
                text += "\n"
            self.ser.write(text.encode("utf-8"))
            return True
        except Exception:
            return False

    

