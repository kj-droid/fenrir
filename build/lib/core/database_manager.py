import sqlite3
import requests
import json
import zipfile
import io
import os
import logging
from datetime import datetime
import git

class DatabaseManager:
    def __init__(self, db_path="data/cve.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("DatabaseManager")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
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
        self.logger.info("Starting CVE database update...")
        current_year = datetime.now().year
        for year in range(current_year - 4, current_year + 1):
            feed_url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.zip"
            self.logger.info(f"Fetching data from {feed_url}")
            try:
                response = requests.get(feed_url, timeout=30)
                response.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    json_filename = z.namelist()[0]
                    with z.open(json_filename) as json_file:
                        cve_data = json.load(json_file)
                        self._parse_and_insert(cve_data)
            except Exception as e:
                self.logger.error(f"Error processing data for year {year}: {e}")
        self.logger.info("CVE database update complete.")

    def _parse_and_insert(self, cve_data):
        cursor = self.conn.cursor()
        vulnerabilities_to_insert = []
        for item in cve_data.get("CVE_Items", []):
            try:
                cve_id = item["cve"]["CVE_data_meta"]["ID"]
                description = item["cve"]["description"]["description_data"][0]["value"]
                published_date = item["publishedDate"]
                cvss_v3_score = None
                severity = "UNKNOWN"
                if "baseMetricV3" in item["impact"]:
                    cvss_v3 = item["impact"]["baseMetricV3"]["cvssV3"]
                    cvss_v3_score = cvss_v3["baseScore"]
                    severity = cvss_v3["baseSeverity"]
                elif "baseMetricV2" in item["impact"]:
                    cvss_v2 = item["impact"]["baseMetricV2"]
                    severity = cvss_v2["severity"]
                vulnerabilities_to_insert.append((cve_id, description, cvss_v3_score, severity, published_date))
            except (KeyError, IndexError) as e:
                self.logger.warning(f"Skipping malformed CVE item: {e}")
                continue
        cursor.executemany('''
            INSERT OR REPLACE INTO vulnerabilities (cve_id, description, cvss_v3_score, severity, published_date)
            VALUES (?, ?, ?, ?, ?)
        ''', vulnerabilities_to_insert)
        self.conn.commit()
        self.logger.info(f"Inserted/Updated {len(vulnerabilities_to_insert)} records.")

    def query_vulnerabilities(self, keyword, min_severity="LOW"):
        cursor = self.conn.cursor()
        severity_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3, "UNKNOWN": 0}
        min_severity_level = severity_map.get(min_severity.upper(), 0)
        results = []
        cursor.execute("SELECT cve_id, description, severity, cvss_v3_score FROM vulnerabilities WHERE description LIKE ?", (f"%{keyword}%",))
        for row in cursor.fetchall():
            cve_id, description, severity, score = row
            current_severity_level = severity_map.get(severity.upper(), 0)
            if current_severity_level >= min_severity_level:
                results.append({"cve_id": cve_id, "description": description, "severity": severity, "cvss_v3_score": score})
        return results

    def update_exploitdb_repo(self):
        """
        Updates the local exploit-db repository used by searchsploit.
        This method is now a placeholder, as searchsploit handles its own updates.
        We recommend running 'searchsploit -u' periodically from the command line.
        """
        self.logger.info("Recommendation: Run 'searchsploit -u' from your terminal to update the exploit database.")
        # The logic to clone the repo is no longer needed here as the `exploitdb` package manages it.
        return True

    def __del__(self):
        self.conn.close()
