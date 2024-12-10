
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.drone_scanner import DroneScanner

class TestDroneScanner(unittest.TestCase):
    def test_run(self):
        scanner = DroneScanner()
        target = "127.0.0.1"
        result = scanner.run(target)
        self.assertIsInstance(result, dict)
        self.assertIn("drone_vulnerabilities", result)

if __name__ == "__main__":
    unittest.main()
