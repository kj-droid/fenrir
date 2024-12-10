import sys
import os
import logging
import argparse
from core.logger import setup_logger
from config.config_manager import ConfigManager
from modules.multi_module_coordinator import MultiModuleCoordinator
from modules.port_scanner import PortScanner
from modules.web_scanner import WebScanner
from modules.vulnerability_identifier import VulnerabilityIdentifier
from modules.exploit_finder import ExploitFinder
from modules.threat_intelligence import ThreatIntelligence


def initialize_logger():
    setup_logger("Fenrir", "logs/activity_log.txt", logging.INFO)
    setup_logger("Errors", "logs/error_log.txt", logging.ERROR)


def initialize_modules():
    """
    Initialize available modules for Fenrir.
    """
    return {
        "portscan": PortScanner(),
        "webscan": lambda target:WebScanner(target),
        "vuln": VulnerabilityIdentifier(),
        "exploit": ExploitFinder(),
        "threat": ThreatIntelligence(),
    }


def parse_arguments():
    """
    Parse command-line arguments for Fenrir.
    """
    parser = argparse.ArgumentParser(description="Fenrir Cyber Security Suite")
    parser.add_argument("--target", required=True, help="Target IP, hostname, or network range")
    parser.add_argument("--modules", required=True, nargs="+", help="Modules to run (space-separated)")
    parser.add_argument("--ports", default="common", help="Port range or list to scan ('common', 'all', or 'custom:ports')")
    parser.add_argument("--output", default="results", help="Output folder for results")
    return parser.parse_args()


def save_results(results, output_folder):
    """
    Save module scan results to the specified output folder.
    """
    os.makedirs(output_folder, exist_ok=True)
    results_file = os.path.join(output_folder, "scan_results.txt")
    with open(results_file, "w") as f:
        for module, result in results.items():
            f.write(f"Module: {module}\n")
            f.write(f"Result: {result}\n")
            f.write("-" * 40 + "\n")
    print(f"Results saved to {output_folder}")


def main():
    """
    Main entry point for Fenrir.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    initialize_logger()
    logger = logging.getLogger("Fenrir")
    logger.info("Fenrir initialized successfully.")

    config_path = "config/config.json"
    config_manager = ConfigManager(config_path)
    config = config_manager.read_config()
    output_folder = config.get("output_folder", "results")

    args = parse_arguments()
    target = args.target
    selected_modules = args.modules
    ports = args.ports

    available_modules = initialize_modules()
    coordinator = MultiModuleCoordinator(available_modules)

    # Validate selected modules
    selected_modules = [module.lower() for module in selected_modules]
    invalid_modules = [module for module in selected_modules if module not in coordinator.list_available_modules()]
    if invalid_modules:
        logger.error(f"Invalid modules: {invalid_modules}")
        sys.exit(f"Error: Invalid modules: {', '.join(invalid_modules)}")

    # Run the selected modules
    logger.info(f"Running selected modules for target: {target}")
    results = coordinator.run_selected_modules(selected_modules, target, ports=ports)
    save_results(results, output_folder)

    logger.info("Scan completed successfully.")
    print("Scan completed. Check the results folder for details.")


if __name__ == "__main__":
    main()
