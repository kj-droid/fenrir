
import json
import logging

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.logger = logging.getLogger("ConfigManager")

    def read_config(self):
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            return {}
