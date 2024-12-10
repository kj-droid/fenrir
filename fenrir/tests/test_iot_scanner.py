
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.iot_scanner import IoTScanner

class TestIoTScanner(unittest.TestCase):
    def test_run(self):
        scanner = IoTScanner()
        target = "127.0.0.1"
        result = scanner.run(target)
        self.assertIsInstance(result, dict)
        self.assertIn("iot_devices", result)

if __name__ == "__main__":
    unittest.main()
