
import logging
from modules.port_scanner import PortScanner
from modules.vulnerability_identifier import VulnerabilityIdentifier
from modules.exploit_finder import ExploitFinder
from modules.threat_intelligence import ThreatIntelligence
from modules.custom_exploit_runner import CustomExploitRunner
from modules.shodan_integration import ShodanIntegration
from modules.metasploit_integration import MetasploitIntegration
from modules.iot_scanner import IoTScanner
from modules.web_scanner import WebScanner
from modules.mobile_scanner import MobileScanner
from modules.drone_scanner import DroneScanner
from modules.cloud_scanner import CloudScanner
from modules.ml_model import MachineLearningModel

class MultiModuleCoordinator:
    def __init__(self, shodan_api_key, msf_client):
        self.modules = {
            "portscan": PortScanner(),
            "vuln": VulnerabilityIdentifier(),
            "exploitfinder": ExploitFinder(),
            "threatintel": ThreatIntelligence(),
            "customexploit": CustomExploitRunner(),
            "shodan": ShodanIntegration(api_key=shodan_api_key),
            "metasploit": MetasploitIntegration(msf_client=msf_client),
            "iot": IoTScanner(),
            "web": WebScanner(),
            "mobile": MobileScanner(),
            "drone": DroneScanner(),
            "cloud": CloudScanner(),
            "ml": MachineLearningModel()
        }
        self.logger = logging.getLogger("MultiModuleCoordinator")

    def list_available_modules(self):
        return list(self.modules.keys())

    def run_selected_modules(self, selected_modules, target, **kwargs):
        results = {}
        for module_name in selected_modules:
            if module_name in self.modules:
                self.logger.info(f"Running module: {module_name} on target: {target}")
                try:
                    module = self.modules[module_name]
                    results[module_name] = module.run(target, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error running module {module_name}: {str(e)}")
                    results[module_name] = {"error": str(e)}
            else:
                self.logger.warning(f"Module {module_name} not found.")
                results[module_name] = {"error": "Module not found"}
        return results
