import sys
import os
import sqlite3
import subprocess

def verify_system():
    """
    Connects to the CVE database and checks if searchsploit is working.
    """
    print("--- Verifying Fenrir Dependencies ---")
    
    cve_db_path = "data/cve.db"
    
    # 1. Check if the CVE database file exists and is populated
    if not os.path.exists(cve_db_path):
        print(f"[FAIL] CVE Database not found at: {cve_db_path}")
        return
        
    try:
        conn_cve = sqlite3.connect(cve_db_path)
        cve_count = conn_cve.execute("SELECT COUNT(*) FROM vulnerabilities").fetchone()[0]
        conn_cve.close()
        print(f"[PASS] CVE Database found with {cve_count} records.")
        if cve_count == 0:
            print("[WARN] CVE database is empty. Please run update_db.py.")
    except Exception as e:
        print(f"[FAIL] Could not query the CVE database: {e}")

    # 2. Check if searchsploit command is found and works
    print("\n--- Verifying searchsploit ---")
    try:
        # Run a simple searchsploit command to test it
        command = ["searchsploit", "--json", "vsftpd"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if "RESULTS_EXPLOIT" in result.stdout:
            print("[PASS] `searchsploit` command is installed and working correctly.")
        else:
            print("[WARN] `searchsploit` ran but found no results for a common term.")
            
    except FileNotFoundError:
        print("[FAIL] `searchsploit` command not found. Please run 'sudo apt install exploitdb'.")
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] `searchsploit` command failed to execute: {e.stderr}")

if __name__ == "__main__":
    verify_system()
