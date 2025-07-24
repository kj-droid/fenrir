import sqlite3
import requests
import json
import zipfile
import io
import os
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/cve.db"):
        """
        Manages the local CVE database using SQLite.
        """
        self.db_path = db_path
        self.logger = logging.getLogger("DatabaseManager")
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        """
        Creates the 'vulnerabilities' table if it doesn't exist.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                cve_id TEXT PRIMARY KEY,
                description TEXT,
                cvss_v3_score REAL,
                severity TEXT,
                published_date TEXT
            )
        ''')
        self.conn.commit()

    def update_database(self):
        """
        Downloads the latest NVD data feeds and updates the database.
        Fetches data for the current year and the 4 previous years.
        """
        self.logger.info("Starting CVE database update...")
        current_year = datetime.now().year
        # Fetch data for the last 5 years (including current)
        for year in range(current_year - 4, current_year + 1):
            feed_url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.zip"
            self.logger.info(f"Fetching data from {feed_url}")
            
            try:
                response = requests.get(feed_url, timeout=30)
                response.raise_for_status() # Raise an exception for bad status codes

                # Unzip and parse the file in memory
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    json_filename = z.namelist()[0]
                    with z.open(json_filename) as json_file:
                        cve_data = json.load(json_file)
                        self._parse_and_insert(cve_data)

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to download data for year {year}: {e}")
            except Exception as e:
                self.logger.error(f"An error occurred while processing data for year {year}: {e}")
        
        self.logger.info("CVE database update complete.")

    def _parse_and_insert(self, cve_data):
        """
        Parses the JSON data from a feed and inserts it into the database.
        """
        cursor = self.conn.cursor()
        vulnerabilities_to_insert = []
        
        for item in cve_data.get("CVE_Items", []):
            cve_id = item["cve"]["CVE_data_meta"]["ID"]
            description = item["cve"]["description"]["description_data"][0]["value"]
            published_date = item["publishedDate"]
            
            cvss_v3_score = None
            severity = "UNKNOWN"
            
            # Prefer CVSS v3 metrics if available
            if "baseMetricV3" in item["impact"]:
                cvss_v3 = item["impact"]["baseMetricV3"]["cvssV3"]
                cvss_v3_score = cvss_v3["baseScore"]
                severity = cvss_v3["baseSeverity"]
            elif "baseMetricV2" in item["impact"]: # Fallback to v2
                cvss_v2 = item["impact"]["baseMetricV2"]
                severity = cvss_v2["severity"]

            vulnerabilities_to_insert.append(
                (cve_id, description, cvss_v3_score, severity, published_date)
            )
        
        # Use executemany for efficient bulk insertion
        cursor.executemany('''
            INSERT OR REPLACE INTO vulnerabilities (cve_id, description, cvss_v3_score, severity, published_date)
            VALUES (?, ?, ?, ?, ?)
        ''', vulnerabilities_to_insert)
        
        self.conn.commit()
        self.logger.info(f"Inserted/Updated {len(vulnerabilities_to_insert)} records.")

    def query_vulnerabilities(self, keyword, min_severity="LOW"):
        """
        Queries the database for vulnerabilities matching a keyword and severity.
        
        Args:
            keyword (str): A keyword (e.g., product name like 'apache' or 'openssh') to search for.
            min_severity (str): The minimum severity to include (e.g., 'MEDIUM', 'HIGH').
            
        Returns:
            list: A list of dictionaries, each representing a found vulnerability.
        """
        cursor = self.conn.cursor()
        severity_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3, "UNKNOWN": 0}
        min_severity_level = severity_map.get(min_severity.upper(), 0)
        
        results = []
        # Query and filter severity in Python as severity levels are text in DB
        cursor.execute("SELECT cve_id, description, severity, cvss_v3_score FROM vulnerabilities WHERE description LIKE ?", (f"%{keyword}%",))
        
        for row in cursor.fetchall():
            cve_id, description, severity, score = row
            current_severity_level = severity_map.get(severity.upper(), 0)
            if current_severity_level >= min_severity_level:
                results.append({
                    "cve_id": cve_id,
                    "description": description,
                    "severity": severity,
                    "cvss_v3_score": score
                })
                
        return results

    def __del__(self):
        """Ensure the database connection is closed when the object is destroyed."""
        self.conn.close()
