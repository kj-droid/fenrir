
import unittest
import sys
import os

# Add the Fenrir project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.port_scanner import PortScanner

class TestPortScanner(unittest.TestCase):
    def test_scan_ports(self):
        scanner = PortScanner(timeout=1)
        target = "127.0.0.1"
        result = scanner.run(target, port_range=(1, 1024))
        self.assertIsInstance(result, dict)
        self.assertTrue(all(isinstance(port, int) for port in result.keys()))

    def test_identify_service(self):
        scanner = PortScanner(timeout=1)
        target = "127.0.0.1"
        service = scanner.identify_service(target, 22)  # Assuming SSH is running locally
        self.assertIsInstance(service, str)

if __name__ == "__main__":
    unittest.main()
