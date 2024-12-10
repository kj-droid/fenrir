
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.mobile_scanner import MobileScanner

class TestMobileScanner(unittest.TestCase):
    def test_run(self):
        scanner = MobileScanner()
        target = "127.0.0.1"
        result = scanner.run(target)
        self.assertIsInstance(result, dict)
        self.assertIn("mobile_issues", result)

if __name__ == "__main__":
    unittest.main()
