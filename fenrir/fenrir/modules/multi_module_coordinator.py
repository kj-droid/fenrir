
import logging

class MultiModuleCoordinator:
    def __init__(self, modules):
        self.modules = modules
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
