import socket
import json
import logging
from typing import Dict, Any, List
from scapy.all import sr1, IP, TCP


class PortScanner:
    """
    A module for scanning open ports and identifying running services.
    """

    def __init__(self, timeout=2, service_mapping_file="data/service_mapping.json"):
        """
        Initialize the PortScanner with a default timeout and service mapping file.
        :param timeout: Timeout for socket connections and scans (in seconds).
        :param service_mapping_file: Path to the JSON file containing port-to-service mappings.
        """
        self.logger = logging.getLogger("PortScanner")
        self.timeout = timeout

        # Load port-to-service mapping
        try:
            with open(service_mapping_file, "r") as f:
                self.service_mapping = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading service mapping: {str(e)}")
            self.service_mapping = {}

    def format_ports_as_ranges(self, ports: List[int]) -> str:
        """
        Format a list of ports as a compact range string.
        :param ports: A list of port numbers.
        :return: A string representing the ports in ranges (e.g., "1-1024, 2048, 3300-4152").
        """
        if not ports:
            return ""

        ports = sorted(ports)
        ranges = []
        start = ports[0]
        end = ports[0]

        for port in ports[1:]:
            if port == end + 1:  # Consecutive port
                end = port
            else:
                # Add the current range to the list
                ranges.append(f"{start}-{end}" if start != end else f"{start}")
                start = port
                end = port

        # Add the last range
        ranges.append(f"{start}-{end}" if start != end else f"{start}")
        return ", ".join(ranges)

    def scan_ports(self, target: str, ports: List[int]) -> Dict[int, str]:
        """
        Scan the specified target for open ports and perform service identification.
        :param target: The target IP or hostname.
        :param ports: A list of ports to scan.
        :return: A dictionary of open ports and identified services.
        """
        port_ranges = self.format_ports_as_ranges(ports)
        self.logger.info(f"Starting port scan on {target} for ports: {port_ranges}.")

        open_ports = {}
        for port in ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(self.timeout)
                    result = s.connect_ex((target, port))
                    if result == 0:
                        service = self.identify_service(target, port)
                        open_ports[port] = service
                        self.logger.info(f"Port {port} is open. Service: {service}")
            except Exception as e:
                self.logger.error(f"Error scanning port {port}: {str(e)}")

        return open_ports

    def identify_service(self, target: str, port: int) -> str:
        """
        Identify the service running on an open port.
        :param target: The target IP or hostname.
        :param port: The port number to identify the service for.
        :return: The name of the detected service or 'Unknown'.
        """
        # Check if the port is in the service mapping
        service = self.service_mapping.get(str(port), "Unknown")

        # Attempt banner grabbing
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((target, port))
                if port == 80 or port == 443:  # HTTP/HTTPS
                    s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                    response = s.recv(1024).decode("utf-8", errors="ignore")
                    if "Server:" in response:
                        return response.split("Server:")[1].split("\r\n")[0].strip()
                elif port == 22:  # SSH
                    banner = s.recv(1024).decode("utf-8", errors="ignore")
                    if "SSH" in banner:
                        return banner.strip()
                elif port == 25:  # SMTP
                    banner = s.recv(1024).decode("utf-8", errors="ignore")
                    if "220" in banner:
                        return "SMTP Server"
        except Exception as e:
            self.logger.warning(f"Service identification failed on port {port}: {str(e)}")

        return service

    def parse_ports(self, port_option: str) -> List[int]:
        """
        Parse a custom port option into a list of ports.
        :param port_option: A string representing ports (e.g., '1-1024,2048,3300-4152').
        :return: A list of unique ports to scan.
        """
        ports = set()
        ranges = port_option.split(",")
        for r in ranges:
            if "-" in r:  # Handle ranges like '1-1024'
                start, end = map(int, r.split("-"))
                ports.update(range(start, end + 1))
            else:  # Handle single ports like '2048'
                ports.add(int(r))
        return sorted(ports)

    def run(self, target: str, port_option: str = "common") -> Dict[str, Any]:
        """
        Run the full port scan, service detection, and OS fingerprinting.
        :param target: The target IP or hostname.
        :param port_option: The port range or list to scan ('common', 'all', or 'custom:ports').
        :return: A dictionary containing scan results.
        """
        results = {
            "target": target,
            "ports": {},
        }

        try:
            # Determine the ports to scan based on user input
            if port_option == "common":
                ports = list(range(1, 1025))  # Default: Common ports
            elif port_option == "all":
                ports = list(range(1, 65536))  # Full port range
            elif port_option.startswith("custom:"):
                custom_ports = port_option.split(":")[1]
                ports = self.parse_ports(custom_ports)  # Parse custom ports
            else:
                raise ValueError("Invalid port option specified.")

            # Perform the scan
            results["ports"] = self.scan_ports(target, ports)
        except Exception as e:
            self.logger.error(f"Error running port scanner: {str(e)}")

        return results
