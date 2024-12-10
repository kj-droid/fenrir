import logging


class MultiModuleCoordinator:
    """
    Coordinates the execution of multiple modules in Fenrir.
    """

    def __init__(self, modules):
        """
        Initialize the MultiModuleCoordinator with available modules.

        :param modules: A dictionary of module names and their classes or factory functions.
        """
        self.modules = modules
        self.logger = logging.getLogger("MultiModuleCoordinator")

    def list_available_modules(self):
        """
        List all available module names.
        """
        return list(self.modules.keys())

    def run_selected_modules(self, selected_modules, target, **kwargs):
        """
        Run the selected modules against the specified target.

        :param selected_modules: List of selected module names to run.
        :param target: The target IP, hostname, or range to scan.
        :param kwargs: Additional arguments to pass to modules.
        :return: A dictionary of results from each module.
        """
        results = {}

        for module_name in selected_modules:
            if module_name in self.modules:
                self.logger.info(f"Running module: {module_name} on target: {target}")
                try:
                    module = self.modules[module_name]
                    # Dynamically handle modules with additional arguments
                    if module_name == "portscan":
                        results[module_name] = module.run(target, port_option=kwargs.get("ports", "common"))
                    elif module_name == "exploitfinder":
                        results[module_name] = module.run(target, vulnerabilities=kwargs.get("vulnerabilities", []))
                    elif module_name == "vulnidentifier":
                        results[module_name] = module.run(target)
                    else:
                        results[module_name] = module.run(target)
                except Exception as e:
                    self.logger.error(f"Error running module {module_name}: {str(e)}")
                    results[module_name] = {"error": str(e)}
            else:
                self.logger.warning(f"Module {module_name} not found.")
                results[module_name] = {"error": "Module not found"}

        return results
