import serial
import serial.tools.list_ports
import threading
import time

class SerialBridge:
    def __init__(self, port_a, port_b, baudrate=9600, log_callback=None):
        self.port_a_name = port_a
        self.port_b_name = port_b
        self.baudrate = baudrate
        self.ser_a = None
        self.ser_b = None
        self.running = False
        self.threads = []
        self.log_callback = log_callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def start(self):
        try:
            self.ser_a = serial.Serial(self.port_a_name, self.baudrate, timeout=0.1)
            self.ser_b = serial.Serial(self.port_b_name, self.baudrate, timeout=0.1)
            self.running = True
            
            # Thread A to B
            t1 = threading.Thread(target=self._bridge, args=(self.ser_a, self.ser_b, "A -> B"), daemon=True)
            # Thread B to A
            t2 = threading.Thread(target=self._bridge, args=(self.ser_b, self.ser_a, "B -> A"), daemon=True)
            
            self.threads = [t1, t2]
            for t in self.threads:
                t.start()
            
            self.log(f"Bridge started: {self.port_a_name} <-> {self.port_b_name} @ {self.baudrate}")
            return True, "Started"
        except Exception as e:
            self.stop()
            return False, str(e)

    def _bridge(self, src, dest, direction):
        while self.running:
            try:
                if src.in_waiting > 0:
                    data = src.read(src.in_waiting)
                    dest.write(data)
                    self.log(f"[{direction}] {len(data)} bytes")
            except Exception as e:
                self.log(f"Error in {direction}: {e}")
                self.running = False
                break
            time.sleep(0.01)

    def stop(self):
        self.running = False
        for t in self.threads:
            t.join(timeout=0.5)
        
        if self.ser_a and self.ser_a.is_open:
            self.ser_a.close()
        if self.ser_b and self.ser_b.is_open:
            self.ser_b.close()
            
        self.log("Bridge stopped.")

    @staticmethod
    def get_available_ports():
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

if __name__ == "__main__":
    # Small test
    available = SerialBridge.get_available_ports()
    print(f"Available ports: {available}")
