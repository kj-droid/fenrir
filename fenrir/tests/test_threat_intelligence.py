
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.threat_intelligence import ThreatIntelligence

class TestThreatIntelligence(unittest.TestCase):
    def test_run(self):
        intel = ThreatIntelligence()
        target = "127.0.0.1"
        result = intel.run(target)
        self.assertIsInstance(result, dict)
        self.assertIn("intel", result)  # Adjusted to check for 'intel' key

if __name__ == "__main__":
    unittest.main()
