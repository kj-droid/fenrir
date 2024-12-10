
import argparse
import logging
from core.logger import setup_logger
from modules.multi_module_coordinator import MultiModuleCoordinator
from core.scheduler import Scheduler

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Fenrir - Modular Vulnerability Scanner")
    parser.add_argument("--target", required=True, help="Target IP, hostname, or URL")
    parser.add_argument("--modules", nargs="+", required=True, help="Modules to run (e.g., portscan, vuln, iot)")
    parser.add_argument("--shodan_key", help="Shodan API key")
    parser.add_argument("--metasploit", action="store_true", help="Enable Metasploit integration")
    args = parser.parse_args()

    # Setup logging
    logger = setup_logger("Fenrir", "logs/activity_log.txt")
    logger.info("Fenrir initialized successfully.")

    # Initialize modules
    shodan_key = args.shodan_key if args.shodan_key else "DEFAULT_SHODAN_API_KEY"
    msf_client = None  # Replace with actual Metasploit RPC client instance if needed

    coordinator = MultiModuleCoordinator(shodan_api_key=shodan_key, msf_client=msf_client)

    # Validate selected modules
    available_modules = coordinator.list_available_modules()
    selected_modules = args.modules
    invalid_modules = [mod for mod in selected_modules if mod not in available_modules]
    if invalid_modules:
        logger.error(f"Invalid modules selected: {invalid_modules}")
        print(f"Error: Invalid modules: {', '.join(invalid_modules)}")
        return

    # Run selected modules
    results = coordinator.run_selected_modules(selected_modules, target=args.target)
    logger.info("Scan completed successfully.")
    print("Scan completed. Check the results folder for details.")

if __name__ == "__main__":
    main()
