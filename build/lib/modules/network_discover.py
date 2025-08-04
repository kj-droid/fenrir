import subprocess
import re
import logging
import os
import shutil
import ipaddress
import netifaces
import nmap

class NetworkDiscover:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_available_interfaces(self):
        """
        Gets a dictionary of all available non-loopback network interfaces 
        and their associated IPv4 and IPv6 CIDR ranges as a clean string.
        """
        interfaces = {}
        try:
            for interface in netifaces.interfaces():
                if interface == 'lo':
                    continue
                
                addrs = netifaces.ifaddresses(interface)
                networks = []
                
                # Handle IPv4
                if netifaces.AF_INET in addrs:
                    for inet_info in addrs[netifaces.AF_INET]:
                        ip_addr = inet_info.get('addr')
                        netmask = inet_info.get('netmask')
                        if ip_addr and netmask:
                            try:
                                network = ipaddress.ip_network(f"{ip_addr}/{netmask}", strict=False)
                                networks.append(str(network.with_prefixlen))
                            except ValueError:
                                self.logger.warning(f"Skipping invalid IPv4 address/netmask on {interface}: {ip_addr}/{netmask}")

                # Handle IPv6
                if netifaces.AF_INET6 in addrs:
                    for inet6_info in addrs[netifaces.AF_INET6]:
                        ip_addr = inet6_info.get('addr')
                        netmask = inet6_info.get('netmask')
                        if ip_addr and netmask:
                            try:
                                clean_ip = ip_addr.split('%')[0]
                                network = ipaddress.ip_network(f"{clean_ip}/{netmask}", strict=False)
                                if not network.is_link_local:
                                    networks.append(str(network.with_prefixlen))
                            except ValueError:
                                self.logger.warning(f"Skipping invalid IPv6 address/netmask on {interface}: {ip_addr}/{netmask}")

                if networks:
                    # --- FIX: Join the list of networks into a single string ---
                    interfaces[interface] = ', '.join(sorted(list(set(networks))))

            return interfaces
        except Exception as e:
            self.logger.error(f"Could not get network interfaces: {e}", exc_info=True)
            return {}

    def run(self, selected_ranges=None):
        """
        Runs an Nmap ping scan (-sn) on the provided network ranges to find live hosts.
        """
        if not selected_ranges:
            return ["ERROR: No network ranges were selected for scanning."]

        all_found_ips = set()
        nm = nmap.PortScanner()

        for network_range in selected_ranges:
            self.logger.info(f"Starting Nmap discovery scan on range: {network_range}")
            try:
                is_ipv6 = ipaddress.ip_network(network_range).version == 6
                arguments = '-sn'
                if is_ipv6:
                    arguments += ' -6'
                
                nm.scan(hosts=network_range, arguments=arguments)
                
                for host in nm.all_hosts():
                    if nm[host].state() == 'up':
                        all_found_ips.add(host)

            except nmap.PortScannerError as e:
                 self.logger.error(f"Nmap discovery scan failed for range {network_range}: {e}")
                 return [f"ERROR: Nmap scan failed. Ensure Nmap is installed and you have permissions."]
            except Exception as e:
                self.logger.error(f"An error occurred during Nmap discovery for range {network_range}: {e}", exc_info=True)
                continue
        
        if not all_found_ips:
            return []

        self.logger.info(f"Discovered {len(all_found_ips)} unique hosts across all networks.")
        return sorted(list(all_found_ips))
