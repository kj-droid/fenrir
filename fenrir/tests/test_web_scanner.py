
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.web_scanner import WebScanner

class TestWebScanner(unittest.TestCase):
    def test_run(self):
        scanner = WebScanner()
        target_url = "http://127.0.0.1"
        result = scanner.run(target_url)
        self.assertIsInstance(result, dict)
        self.assertIn("web_vulnerabilities", result)

if __name__ == "__main__":
    unittest.main()
