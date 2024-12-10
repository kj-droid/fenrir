import json
import os
import logging

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.logger = logging.getLogger("ConfigManager")
        
    def _ensure_config_file(self):
        """
        Ensure the configuration file exists; create it with defaults if not.
        """
        if not os.path.exists(self.config_file):
            default_config = {
                "api_keys": {
                    "alienvault": "",
                    "virustotal": ""
                },
                "default_scan_settings": {
                    "port_range": "1-65535",
                    "thread_count": 100,
                    "output_folder": "reports/output"
                },
                "modules": {
                    "port_scanner": True,
                    "vulnerability_identifier": True,
                    "exploit_finder": True,
                    "web_scanner": True,
                    "threat_intelligence": True
                }
            }
            with open(self.config_file, "w") as file:
                json.dump(default_config, file, indent=4)

    def read_config(self):
        """
        Read and return the configuration.
        :return: Dictionary of configuration data.
        """
        try:
            with open(self.config_file, "r") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error reading config file: {e}")
            return {}

    def update_config(self, key, value):
        """
        Update a specific key in the configuration.
        :param key: Key to update (e.g., "api_keys.alienvault").
        :param value: New value for the key.
        """
        config = self.read_config()
        keys = key.split(".")
        sub_config = config
        for k in keys[:-1]:
            sub_config = sub_config.setdefault(k, {})
        sub_config[keys[-1]] = value

        try:
            with open(self.config_file, "w") as file:
                json.dump(config, file, indent=4)
            print(f"Configuration updated: {key} = {value}")
        except Exception as e:
            print(f"Error updating config file: {e}")


if __name__ == "__main__":
    # Example usage
    config_manager = ConfigManager()

    # Read configuration
    config = config_manager.read_config()
    print("Current Configuration:", config)

    # Update API key for AlienVault
    config_manager.update_config("api_keys.alienvault", "NEW_ALIENVAULT_API_KEY")

    # Update default thread count
    config_manager.update_config("default_scan_settings.thread_count", 200)
