import json
import os
import logging

class ConfigManager:
    def __init__(self, config_file="config/config.json"):
        self.config_file = config_file
        self.logger = logging.getLogger("ConfigManager")
        self._ensure_config_file()

    def _ensure_config_file(self):
        """
        Ensure the configuration file exists; create it with defaults if not.
        """
        if not os.path.exists(self.config_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            default_config = {
                "api_keys": { "alienvault": "", "virustotal": "" },
                "default_scan_settings": {
                    "port_range": "1-1024",
                    "output_folder": "reports/output"
                }
            }
            with open(self.config_file, "w") as file:
                json.dump(default_config, file, indent=4)
            self.logger.info(f"Default config file created at {self.config_file}")

    def read_config(self):
        """ Read and return the configuration. """
        try:
            with open(self.config_file, "r") as file:
                return json.load(file)
        except Exception as e:
            self.logger.error(f"Error reading config file: {e}")
            return {}
