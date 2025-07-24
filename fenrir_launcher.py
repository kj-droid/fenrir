import sys
import os

# Add the project root directory to the Python path
# This ensures that all modules can be imported correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import argparse

from PyQt5.QtWidgets import QApplication
from gui.fenrir_gui import FenrirGUI
from fenrir_cli import run_cli

def main():
    """
    Main entry point for Fenrir.
    Launches either the GUI or CLI based on user arguments.
    """
    parser = argparse.ArgumentParser(description="Fenrir: Multi-Module Security Scanner")
    parser.add_argument(
        '--mode',
        choices=['gui', 'cli'],
        default='gui',
        help="Mode to run Fenrir in (gui or cli). Defaults to gui."
    )

    # Parse only the --mode argument first
    args, remaining_args = parser.parse_known_args()

    if args.mode == 'gui':
        print("Launching Fenrir GUI...")
        app = QApplication(sys.argv)
        window = FenrirGUI()
        window.show()
        sys.exit(app.exec_())
    else:
        print("Running Fenrir in CLI mode...")
        # Pass the rest of the arguments to the CLI handler
        run_cli(remaining_args)

if __name__ == "__main__":
    main()
