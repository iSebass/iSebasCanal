import serial
import serial.tools.list_ports
import threading
import time
import queue
import paho.mqtt.client as mqtt
import random
import re
from config_manager import ConfigManager

import unicodedata

def slugify(text):
    # Normalize unicode characters to decompose combined characters (like á to a + ´)
    text = unicodedata.normalize('NFD', text)
    # Filter out non-spacing mark characters (the accents)
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    # Standard slugify logic
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '_', text).strip('_')

class GatewayBridge:
    def __init__(self, loop, on_data=None, on_status=None):
        self.loop = loop
        self.on_data = on_data
        self.on_status = on_status
        self.running = False
        self.serial_conn = None
        self.config = ConfigManager.load()
        self.serial_thread = None
        self.mqtt_thread = None
        self.simulation_mode = False
        self.data_queue = queue.Queue()
        
        # Initialize Paho MQTT Client
        # Use CallbackAPIVersion.VERSION2 for paho-mqtt 2.0+
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect

    def _on_mqtt_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("DEBUG: MQTT Connected successfully.")
            self.set_status("mqtt", "connected", "Active")
        else:
            print(f"DEBUG: MQTT Connection failed with code {rc}")
            self.set_status("mqtt", "error", f"Conn Error: {rc}")

    def _on_mqtt_disconnect(self, client, userdata, disconnect_flags, rc, properties):
        print(f"DEBUG: MQTT Disconnected (code {rc})")
        if self.running:
            self.set_status("mqtt", "reconnecting", "Reconnecting...")

    def set_status(self, service, state, message=""):
        if self.on_status:
            self.loop.call_soon_threadsafe(
                lambda: self.on_status(service, state, message)
            )

    def start(self, simulation=False):
        self.running = True
        self.simulation_mode = simulation
        
        # Start MQTT loop in its own thread (paho handles this)
        cfg = ConfigManager.load()["mqtt"]
        if cfg["username"] and cfg["password"]:
            self.mqtt_client.username_pw_set(cfg["username"], cfg["password"])
        
        try:
            self.mqtt_client.connect(cfg["broker"], cfg["port"], 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            print(f"DEBUG: Initial MQTT connect error: {e}")
            self.set_status("mqtt", "error", str(e))

        if simulation:
            self.serial_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        else:
            self.serial_thread = threading.Thread(target=self._serial_loop, daemon=True)
        
        self.mqtt_thread = threading.Thread(target=self._mqtt_worker, daemon=True)
        
        self.serial_thread.start()
        self.mqtt_thread.start()

    def _simulation_loop(self):
        self.set_status("serial", "connected", "SIMULATION ACTIVE")
        while self.running:
            vals = [round(random.uniform(20.0, 30.0), 1), round(random.uniform(40.0, 70.0), 1), 
                    random.randint(1000, 1020), random.randint(400, 500)]
            data_str = "/".join(map(str, vals))
            payload = {"raw": f"*{data_str}#", "values": [str(v) for v in vals], "timestamp": time.time()}
            
            if self.on_data:
                # Notify UI via loop
                p = payload.copy()
                self.loop.call_soon_threadsafe(lambda: self.on_data(p))
            
            self.data_queue.put(payload)
            time.sleep(2)

    def _serial_loop(self):
        while self.running:
            try:
                self.config = ConfigManager.load()
                port = self.config["serial"]["port"]
                baud = self.config["serial"]["baud"]
                self.set_status("serial", "connecting", f"Connecting to {port}")
                self.serial_conn = serial.Serial(port, baud, timeout=1)
                self.set_status("serial", "connected", "Active")
                
                buffer = ""
                while self.running:
                    if self.serial_conn.in_waiting > 0:
                        char = self.serial_conn.read().decode('ascii', errors='ignore')
                        buffer += char
                        if '#' in buffer:
                            start, end = buffer.find('*'), buffer.find('#')
                            if start != -1 and end > start:
                                data_str = buffer[start+1:end]
                                sensors = [v.strip() for v in data_str.split('/') if v.strip()]
                                payload = {"raw": f"*{data_str}#", "values": sensors, "timestamp": time.time()}
                                
                                if self.on_data:
                                    p = payload.copy()
                                    self.loop.call_soon_threadsafe(lambda: self.on_data(p))
                                
                                self.data_queue.put(payload)
                                buffer = buffer[end+1:]
                            else:
                                if end != -1: buffer = buffer[end+1:]
                    time.sleep(0.01)
            except Exception as e:
                self.set_status("serial", "reconnecting", f"Error: {str(e)}")
                if self.serial_conn: self.serial_conn.close()
                time.sleep(5)

    def _mqtt_worker(self):
        print("DEBUG: MQTT Worker thread started.")
        while self.running:
            try:
                data = self.data_queue.get(timeout=1)
                cfg = ConfigManager.load()
                mqtt_cfg = cfg["mqtt"]
                sensors_cfg = cfg.get("sensors", [])
                base = mqtt_cfg["base_topic"]
                
                for idx, val in enumerate(data["values"]):
                    # Find custom name or fallback to sensorN
                    if idx < len(sensors_cfg) and sensors_cfg[idx].get("name"):
                        sensor_slug = slugify(sensors_cfg[idx]["name"])
                    else:
                        sensor_slug = f"sensor{idx+1}"
                        
                    topic = f"{base}/{sensor_slug}"
                    print(f"DEBUG: Publishing to topic: {topic}")
                    self.mqtt_client.publish(topic, payload=val)
                
                self.data_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"DEBUG: MQTT Worker Error: {e}")
                time.sleep(2)

    def stop(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
        
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        
        self.set_status("serial", "offline", "Detenido")
        self.set_status("mqtt", "offline", "Detenido")

