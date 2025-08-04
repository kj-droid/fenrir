from modules.port_scanner import PortScanner
from modules.vulnerability_identifier import VulnerabilityIdentifier
from modules.exploit_finder import ExploitFinder

class ModuleCoordinator:
    def __init__(self):
        self.module_sequence = [
            "port_scanner",
            "vulnerability_identifier",
            "exploit_finder",
        ]
        self.available_modules = self._initialize_modules()

    def _initialize_modules(self):
        return {
            "port_scanner": PortScanner(),
            "vulnerability_identifier": VulnerabilityIdentifier(),
            "exploit_finder": ExploitFinder(),
        }

    def get_available_module_names(self):
        return list(self.available_modules.keys())

    def run_selected_modules(self, modules_to_run, target, ports="1-1024", initial_results=None):
        """
        Runs selected modules, starting with any initial results provided.
        """
        cumulative_results = initial_results if initial_results is not None else {}
        final_results = initial_results if initial_results is not None else {}

        for module_name in self.module_sequence:
            if module_name in modules_to_run:
                module = self.available_modules[module_name]
                try:
                    # The port scanner's main 'run' method will overwrite the discovery data
                    # with more detailed port info, which is the desired behavior.
                    result = module.run(
                        target=target, 
                        ports=ports, 
                        previous_results=cumulative_results
                    )
                    final_results[module_name] = result
                    cumulative_results[module_name] = result
                except Exception as e:
                    error_message = f"Error in module {module_name}: {e}"
                    final_results[module_name] = error_message
                    break
        
        return final_results
