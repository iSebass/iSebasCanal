import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "serial": {
        "port": "COM3",
        "baud": 9600
    },
    "mqtt": {
        "broker": "broker.emqx.io",
        "port": 1883,
        "username": "user",
        "password": "pass",
        "base_topic": "sensores/planta1"
    }
}

class ConfigManager:
    @staticmethod
    def load():
        if not os.path.exists(CONFIG_FILE):
            ConfigManager.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG

    @staticmethod
    def save(config):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
