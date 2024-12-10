import socket
import logging
import json
import os
from concurrent.futures import ThreadPoolExecutor


class DroneScanner:
    def __init__(self, target, port_range=(1, 65535), timeout=2, output_dir="reports/output"):
        """
        Initialize the DroneScanner.
        :param target: Target IP address or hostname of the drone or controller.
        :param port_range: Range of ports to scan (default: 1-65535).
        :param timeout: Timeout for socket connections in seconds.
        :param output_dir: Directory to save scan results.
        """
        self.target = target
        self.port_range = port_range
        self.timeout = timeout
        self.output_dir = output_dir
        self.open_ports = []
        self.logger = logging.getLogger("DroneScanner")
        logging.basicConfig(level=logging.INFO)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def scan_drone_ports(self, drone_ports):
        """
        Scan drone-specific ports to identify open services.
        :param drone_ports: List of common drone communication ports.
        :return: List of open ports.
        """
        self.logger.info(f"Scanning drone-specific ports on {self.target}...")
        discovered_ports = []

        def scan_port(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(self.timeout)
                    result = sock.connect_ex((self.target, port))
                    if result == 0:
                        self.logger.info(f"Port {port} is open.")
                        discovered_ports.append(port)
            except Exception as e:
                self.logger.warning(f"Error scanning port {port}: {e}")

        with ThreadPoolExecutor() as executor:
            executor.map(scan_port, drone_ports)

        self.logger.info("Drone-specific port scanning completed.")
        return discovered_ports

    def identify_protocol(self, port):
        """
        Attempt to identify the protocol or service running on a specific drone-related port.
        :param port: Open port to analyze.
        :return: Protocol name or description.
        """
        protocols = {
            5760: "MAVLink",
            14550: "MAVLink (UDP)",
            554: "RTSP",
            500: "IKE (VPN)",
            161: "SNMP",
            80: "HTTP",
            443: "HTTPS"
        }
        return protocols.get(port, "Unknown Protocol")

    def scan_drone_vulnerabilities(self, open_ports):
        """
        Scan for known vulnerabilities on drone-specific ports.
        :param open_ports: List of open ports to check for vulnerabilities.
        :return: List of potential vulnerabilities.
        """
        self.logger.info("Scanning for drone-specific vulnerabilities...")
        vulnerabilities = []
        for port in open_ports:
            protocol = self.identify_protocol(port)
            if protocol in ["MAVLink", "RTSP", "SNMP"]:
                vulnerabilities.append({
                    "port": port,
                    "protocol": protocol,
                    "issue": f"{protocol} may be misconfigured or vulnerable to attacks."
                })
        return vulnerabilities

    def save_results(self, open_ports, vulnerabilities, output_file="drone_scan_results.json"):
        """
        Save drone scan results to a JSON file.
        :param open_ports: List of open ports.
        :param vulnerabilities: List of identified vulnerabilities.
        :param output_file: Name of the output file.
        """
        file_path = os.path.join(self.output_dir, output_file)
        results = {
            "target": self.target,
            "open_ports": open_ports,
            "vulnerabilities": vulnerabilities,
        }
        try:
            with open(file_path, "w") as file:
                json.dump(results, file, indent=4)
            self.logger.info(f"Drone scan results saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")


if __name__ == "__main__":
    # Example usage
    target = "192.168.1.150"
    drone_scanner = DroneScanner(target=target, port_range=(1, 1024))

    # Scan drone-specific ports
    drone_ports = [5760, 14550, 554, 500, 161, 80, 443]
    open_ports = drone_scanner.scan_drone_ports(drone_ports)

    # Identify vulnerabilities
    vulnerabilities = drone_scanner.scan_drone_vulnerabilities(open_ports)

    # Save results
    drone_scanner.save_results(open_ports, vulnerabilities)

    # Print results
    print("\nOpen Ports:")
    print(open_ports)
    print("\nIdentified Vulnerabilities:")
    for vuln in vulnerabilities:
        print(f"Port {vuln['port']} ({vuln['protocol']}): {vuln['issue']}")
