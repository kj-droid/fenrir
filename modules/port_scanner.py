from .base_module import BaseModule
import nmap
import logging

class PortScanner(BaseModule):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.name)

    def run(self, target, ports="1-1024", previous_results=None):
        """
        Performs a port scan using nmap with service and version detection.
        """
        self.logger.info(f"Starting version scan on {target} for ports: {ports}")
        nm = nmap.PortScanner()
        
        # Use -sV for version detection. This requires root privileges on some systems.
        # The arguments can be adjusted for more/less aggressive scanning.
        try:
            nm.scan(target, ports, arguments='-sV')
        except nmap.PortScannerError as e:
            self.logger.error(f"Nmap scan failed: {e}. Ensure nmap is installed and you have sufficient privileges.")
            return "Nmap scan failed. Check logs for details."

        scan_results = {}
        try:
            for host in nm.all_hosts():
                self.logger.info(f"Host: {host} ({nm[host].hostname()})")
                scan_results[host] = {'ports': []}

                for proto in nm[host].all_protocols():
                    lport = nm[host][proto].keys()
                    for port in sorted(lport):
                        service_info = nm[host][proto][port]
                        port_details = {
                            'port': port,
                            'state': service_info.get('state'),
                            'name': service_info.get('name', ''),
                            'product': service_info.get('product', ''),
                            'version': service_info.get('version', ''),
                            'extrainfo': service_info.get('extrainfo', ''),
                        }
                        scan_results[host]['ports'].append(port_details)
                        self.logger.info(f"Port {port} is {port_details['state']} - Service: {port_details['product']} {port_details['version']}")

            return scan_results if scan_results else "No open ports or services found."
        except KeyError:
            self.logger.warning(f"Scan for {target} returned no valid host data. The host may be down or blocking scans.")
            return "Scan failed or host is down."
