from .base_module import BaseModule
import nmap
import logging
import os

class PortScanner(BaseModule):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    def discover_host(self, target):
        """
        Performs a robust preliminary scan to check if the host is online and detect its OS.
        This scan now assumes Nmap has the necessary permissions for OS detection.
        -PS: TCP SYN Ping
        -PA: TCP ACK Ping
        -PU: UDP Ping
        -O: Enable OS detection
        """
        self.logger.info(f"Discovering host: {target}")
        nm = nmap.PortScanner()
        discovery_results = {'status': 'down', 'os': 'unknown', 'hostname': 'unknown-host'}
        
        # --- FIX: Always attempt the more powerful OS detection scan ---
        # The setup script is now responsible for setting the required permissions.
        arguments = '-PS -PA -PU -O'

        try:
            self.logger.debug(f"Executing Nmap discovery with arguments: '{arguments}' on target: {target}")
            nm.scan(hosts=target, arguments=arguments)
            if target in nm.all_hosts():
                state = nm[target].state()
                if state == 'up':
                    discovery_results['status'] = 'up'
                    discovery_results['hostname'] = nm[target].hostname() if nm[target].hostname() else 'unknown-host'
                    if 'osmatch' in nm[target] and nm[target]['osmatch']:
                        os_match = nm[target]['osmatch'][0]
                        discovery_results['os'] = f"{os_match['name']} ({os_match['accuracy']}%)"
        except nmap.PortScannerError as e:
            self.logger.error(f"Host discovery scan failed for {target}: {e}")
            if "requires root privileges" in str(e):
                self.logger.error("Nmap requires root privileges for OS detection. Please re-run the setup script with sudo.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during host discovery for {target}: {e}", exc_info=True)
            
        self.logger.info(f"Discovery results for {target}: {discovery_results}")
        return discovery_results

    def run(self, target, ports="1-1024", previous_results=None):
        """
        Performs a full port scan. In the current workflow, host discovery is
        handled by the ScanWorker, so this method proceeds directly to the detailed scan.
        """
        self.logger.info(f"Host {target} is up. Starting detailed port scan.")
        nm = nmap.PortScanner()
        full_results = {target: {}}
        
        try:
            nm.scan(target, ports, arguments='-sV') # -sV for version detection
            if target in nm.all_hosts():
                full_results[target]['hostname'] = nm[target].hostname() if nm[target].hostname() else 'unknown-host'
                full_results[target]['ports'] = []
                for proto in nm[target].all_protocols():
                    lport = sorted(nm[target][proto].keys())
                    for port in lport:
                        service_info = nm[target][proto][port]
                        full_results[target]['ports'].append({
                            'port': port, 'state': service_info.get('state'),
                            'name': service_info.get('name', ''), 'product': service_info.get('product', ''),
                            'version': service_info.get('version', ''), 'extrainfo': service_info.get('extrainfo', '')
                        })
        except Exception as e:
            self.logger.error(f"Detailed port scan failed for {target}: {e}", exc_info=True)
            full_results[target]['error'] = "Detailed port scan failed."

        return full_results
