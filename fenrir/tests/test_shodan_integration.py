
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.shodan_integration import ShodanIntegration

class TestShodanIntegration(unittest.TestCase):
    def test_run(self):
        shodan_key = "TEST_API_KEY"  # Replace with a valid test API key if needed
        integration = ShodanIntegration(api_key=shodan_key)
        target = "8.8.8.8"
        result = integration.run(target)
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)  # Assuming invalid API keys return an error key

if __name__ == "__main__":
    unittest.main()
