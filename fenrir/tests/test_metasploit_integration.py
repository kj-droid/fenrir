
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.metasploit_integration import MetasploitIntegration

class TestMetasploitIntegration(unittest.TestCase):
    def test_run(self):
        # Mock Metasploit client (replace with actual client for full test)
        mock_client = None
        integration = MetasploitIntegration(msf_client=mock_client)
        target = "127.0.0.1"
        result = integration.run(target)
        self.assertIsInstance(result, dict)
        self.assertIn("result", result)  # Adjusted to check for 'result' key

if __name__ == "__main__":
    unittest.main()
