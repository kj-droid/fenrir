from modules.port_scanner import PortScanner
from modules.vulnerability_identifier import VulnerabilityIdentifier
from modules.exploit_finder import ExploitFinder
# Import other modules as you create them

class ModuleCoordinator:
    def __init__(self):
        self.available_modules = self._initialize_modules()

    def _initialize_modules(self):
        """Initializes all available scanning modules."""
        return {
            "port_scanner": PortScanner(),
            "vulnerability_identifier": VulnerabilityIdentifier(),
            "exploit_finder": ExploitFinder(),
        }

    def get_available_module_names(self):
        return list(self.available_modules.keys())

    def run_selected_modules(self, modules_to_run, target, ports="1-1024"):
        """
        Runs the selected modules against a target.
        """
        results = {}
        # This will hold results from modules like port_scanner to be passed to others
        shared_results = {}

        for module_name in modules_to_run:
            if module_name in self.available_modules:
                module = self.available_modules[module_name]
                try:
                    result = module.run(target=target, ports=ports, previous_results=shared_results)
                    results[module_name] = result
                    # Update shared_results with the new findings
                    if isinstance(result, dict):
                         shared_results.update(result)
                except Exception as e:
                    results[module_name] = f"Error running module {module_name}: {e}"
            else:
                results[module_name] = "Module not found."
        return results
