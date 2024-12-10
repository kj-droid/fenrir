
import logging
import socket

class PortScanner:
    def __init__(self, timeout=2):
        self.timeout = timeout
        self.logger = logging.getLogger("PortScanner")

    def identify_service(self, target, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((target, port))
                banner = s.recv(1024).decode("utf-8", errors="ignore")
                return banner.strip()
        except Exception:
            return "Unknown"

    def run(self, target, port_range=(1, 1024)):
        self.logger.info(f"Starting port scan on {target} for ports {port_range[0]}-{port_range[1]}.")
        results = {}
        for port in range(port_range[0], port_range[1] + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(self.timeout)
                    if s.connect_ex((target, port)) == 0:
                        service = self.identify_service(target, port)
                        results[port] = {"service": service}
            except Exception as e:
                self.logger.error(f"Error scanning port {port}: {str(e)}")
        return results
