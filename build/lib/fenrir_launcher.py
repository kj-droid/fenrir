import sys
import os
import argparse
import logging
import traceback

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.logger import setup_logger

# --- Global Exception Handler ---
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    This function will be called for any unhandled exception.
    It logs the error and displays a user-friendly crash report dialog.
    """
    error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.critical(f"Unhandled exception caught:\n{error_message}")
    
    # We only try to show a GUI dialog if PyQt5 is available
    try:
        from PyQt5.QtWidgets import QMessageBox, QApplication
        
        app = QApplication.instance() or QApplication(sys.argv)
        
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("Fenrir has encountered a critical error and must close.")
        error_dialog.setInformativeText("Please see the details below. A full report has been saved to logs/debug.log.")
        error_dialog.setDetailedText(error_message)
        error_dialog.setWindowTitle("Fenrir - Crash Report")
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()
    except ImportError:
        # Fallback for non-GUI crashes or if PyQt5 is part of the problem
        print("A critical error occurred. Please check the logs/debug.log file for details.", file=sys.stderr)

def main():
    """
    Main entry point for Fenrir.
    Launches either the GUI or CLI based on user arguments.
    """
    setup_logger(log_level=logging.DEBUG)
    
    # Set the global exception hook
    sys.excepthook = handle_uncaught_exception
    
    parser = argparse.ArgumentParser(description="Fenrir: Multi-Module Security Scanner")
    parser.add_argument(
        '--mode',
        choices=['gui', 'cli'],
        default='gui',
        help="Mode to run Fenrir in (gui or cli). Defaults to gui."
    )

    args, remaining_args = parser.parse_known_args()

    if args.mode == 'gui':
        # These imports are moved inside the 'if' block to avoid
        # loading GUI components for the CLI mode.
        from gui.fenrir_gui import FenrirGUI
        from PyQt5.QtWidgets import QApplication

        logging.info("Launching Fenrir GUI...")
        app = QApplication(sys.argv)
        window = FenrirGUI()
        window.show()
        sys.exit(app.exec_())
    else:
        from fenrir_cli import run_cli
        # For CLI mode, we don't need the graphical crash handler
        sys.excepthook = sys.__excepthook__
        logging.info("Running Fenrir in CLI mode...")
        run_cli(remaining_args)

if __name__ == "__main__":
    main()
