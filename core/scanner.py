import socket
import logging
from concurrent.futures import ThreadPoolExecutor


class Scanner:
    def __init__(self, target, port_range=(1, 65535), timeout=2):
        """
        Initialize the Scanner.
        :param target: Target IP address or hostname.
        :param port_range: Tuple specifying the port range to scan (default: 1-65535).
        :param timeout: Timeout for socket connections in seconds.
        """
        self.target = target
        self.port_range = port_range
        self.timeout = timeout
        self.open_ports = []
        self.logger = logging.getLogger("Scanner")
        logging.basicConfig(level=logging.INFO)

    def scan_port(self, port):
        """
        Scan a single port to check if it's open.
        :param port: Port number to scan.
        :return: Tuple (port, is_open)
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((self.target, port))
                if result == 0:
                    self.logger.info(f"Port {port} is open.")
                    return port, True
        except Exception as e:
            self.logger.error(f"Error scanning port {port}: {e}")
        return port, False

    def run_scan(self, max_threads=100):
        """
        Run the port scan for the specified target and port range.
        :param max_threads: Maximum number of threads for concurrent scanning.
        :return: List of open ports.
        """
        self.logger.info(f"Starting scan for {self.target} on ports {self.port_range[0]}-{self.port_range[1]}...")
        with ThreadPoolExecutor(max_threads) as executor:
            results = executor.map(self.scan_port, range(self.port_range[0], self.port_range[1] + 1))

        for port, is_open in results:
            if is_open:
                self.open_ports.append(port)

        self.logger.info(f"Scan completed. Open ports: {self.open_ports}")
        return self.open_ports

    def service_mapping(self, service_map_file="data/service_mapping.json"):
        """
        Map open ports to common services using a service mapping file.
        :param service_map_file: Path to a JSON file containing port-to-service mappings.
        :return: Dictionary mapping ports to services.
        """
        try:
            import json
            with open(service_map_file, "r") as file:
                service_map = json.load(file)
            mapped_services = {port: service_map.get(str(port), "Unknown Service") for port in self.open_ports}
            self.logger.info(f"Mapped services: {mapped_services}")
            return mapped_services
        except Exception as e:
            self.logger.error(f"Error loading service mapping: {e}")
            return {port: "Unknown Service" for port in self.open_ports}

    def load_passwords(wordlist_path="data/wordlists/passwords.txt"):
        """
        Load passwords from the specified wordlist.
        :param wordlist_path: Path to the password wordlist.
        :return: List of passwords.
        """
        try:
            with open(wordlist_path, "r") as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            logger.error(f"Wordlist not found: {wordlist_path}")
            return []

    def brute_force_login(target, usernames, wordlist="data/wordlists/passwords.txt"):
        """
        Perform password brute-forcing on the target.
        :param target: Target service or URL.
        :param usernames: List of usernames to test.
        :param wordlist: Path to the password wordlist.
        """
        passwords = load_passwords(wordlist)
        for username in usernames:
            for password in passwords:
                if attempt_login(target, username, password):  # Replace with your login logic
                    print(f"Successful login: {username}:{password}")
                    return True
        print("Brute force failed.")
        return False

    def load_directories(wordlist_path="data/wordlists/directories.txt"):
        """
        Load directories from the specified wordlist.
        :param wordlist_path: Path to the directory wordlist.
        :return: List of directories.
        """
        try:
            with open(wordlist_path, "r") as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            logger.error(f"Wordlist not found: {wordlist_path}")
            return []

    def directory_brute_force(target_url, wordlist="data/wordlists/directories.txt"):
        """
        Perform directory brute-forcing on a target URL.
        :param target_url: Base URL of the target.
        :param wordlist: Path to the directory wordlist.
        """
        directories = load_directories(wordlist)
        for directory in directories:
            url = f"{target_url}/{directory}"
            response = requests.head(url)
            if response.status_code == 200:
                print(f"Found: {url}")






if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simple port scanner.")
    parser.add_argument("target", help="Target IP address or hostname")
    parser.add_argument("--ports", help="Port range (e.g., 1-1000)", default="1-65535")
    parser.add_argument("--timeout", help="Timeout for port scans (seconds)", type=float, default=2)
    args = parser.parse_args()

    # Parse port range
    port_range = tuple(map(int, args.ports.split("-")))

    # Run scanner
    scanner = Scanner(target=args.target, port_range=port_range, timeout=args.timeout)
    open_ports = scanner.run_scan()

    # Map services
    services = scanner.service_mapping()
    print("\nOpen Ports and Services:")
    for port, service in services.items():
        print(f"Port {port}: {service}")
