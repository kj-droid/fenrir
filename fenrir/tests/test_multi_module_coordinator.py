
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.multi_module_coordinator import MultiModuleCoordinator

class TestMultiModuleCoordinator(unittest.TestCase):
    def test_run_selected_modules(self):
        coordinator = MultiModuleCoordinator(shodan_api_key="TEST_API_KEY", msf_client=None)
        target = "127.0.0.1"
        selected_modules = ["portscan", "vuln", "exploitfinder"]
        results = coordinator.run_selected_modules(selected_modules, target)
        
        self.assertIsInstance(results, dict)
        for module in selected_modules:
            self.assertIn(module, results)
            self.assertIsInstance(results[module], dict)

if __name__ == "__main__":
    unittest.main()
