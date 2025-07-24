# update_db.py
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.database_manager import DatabaseManager
from utils.logger import setup_logger

def main():
    """
    Standalone script to update the CVE database.
    """
    # Setup logger
    setup_logger()
    
    print("Initializing Database Manager to update the CVE database.")
    print("This may take several minutes depending on your connection speed...")
    
    db_manager = DatabaseManager()
    db_manager.update_database()
    
    print("Database update process has finished.")

if __name__ == "__main__":
    main()
