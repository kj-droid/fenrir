import argparse
from core.module_coordinator import ModuleCoordinator

def run_cli(args=None):
    """
    Handles the command-line interface logic for Fenrir.
    """
    parser = argparse.ArgumentParser(description="Fenrir CLI Mode")
    parser.add_argument("--target", required=True, help="Target IP, hostname, or network range")
    parser.add_argument("--modules", required=True, nargs="+", help="Modules to run (e.g., port_scanner exploit_finder)")
    parser.add_argument("--ports", default="1-1024", help="Port range for scans (e.g., '1-1024', 'all')")

    parsed_args = parser.parse_args(args)

    coordinator = ModuleCoordinator()

    print(f"Starting scan on target: {parsed_args.target}")
    print(f"Modules selected: {', '.join(parsed_args.modules)}")

    # Run the scan via the coordinator
    results = coordinator.run_selected_modules(
        modules_to_run=parsed_args.modules,
        target=parsed_args.target,
        ports=parsed_args.ports
    )

    if results:
        print("\nScan Results:")
        for module, result in results.items():
            print(f"\n--- {module} ---")
            print(result)
        print("\nScan complete.")
    else:
        print("Scan finished with no results.")
