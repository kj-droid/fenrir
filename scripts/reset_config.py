import os
import json


def reset_config(config_file="config/config.json"):
    """
    Reset the configuration file to its default state.
    :param config_file: Path to the configuration file.
    """
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

    try:
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, "w") as file:
            json.dump(default_config, file, indent=4)
        print(f"Configuration reset to default and saved to {config_file}")
    except Exception as e:
        print(f"Error resetting configuration: {e}")


if __name__ == "__main__":
    reset_config()
