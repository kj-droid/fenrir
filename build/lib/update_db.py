import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.database_manager import DatabaseManager
from utils.logger import setup_logger

def main():
    """
    Standalone script to update data sources for Fenrir.
    """
    setup_logger()
    
    print("Initializing Database Manager...")
    db_manager = DatabaseManager()
    
    print("\n--- Updating NVD CVE Database ---")
    db_manager.update_database()
    
    # The exploit-db update is now a manual recommendation
    print("\n--- Exploit Database Update ---")
    print("To keep exploits current, please run this command periodically:")
    print("sudo searchsploit -u")
    
    print("\nAll data source updates are complete.")

if __name__ == "__main__":
    main()
