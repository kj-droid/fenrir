
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.cloud_scanner import CloudScanner

class TestCloudScanner(unittest.TestCase):
    def test_run(self):
        scanner = CloudScanner()
        target = "127.0.0.1"
        result = scanner.run(target)
        self.assertIsInstance(result, dict)
        self.assertIn("cloud_issues", result)

if __name__ == "__main__":
    unittest.main()
