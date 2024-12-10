
import os
import json
import gzip
import requests
import sqlite3

class CVEFeedDownloader:
    def __init__(self, db_path="data/nvd_local_db.sqlite", feed_base_url="https://nvd.nist.gov/feeds/json/cve/1.1/"):
        self.db_path = db_path
        self.feed_base_url = feed_base_url
        self.feed_years = list(range(2002, 2024))  # Add or update years as needed

    def initialize_database(self):
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cves (
                    cve_id TEXT PRIMARY KEY,
                    description TEXT,
                    published_date TEXT,
                    last_modified_date TEXT,
                    impact TEXT
                )
            ''')
            conn.commit()
            conn.close()
            print("Database initialized.")

    def download_and_extract_feed(self, year):
        feed_url = f"{self.feed_base_url}nvdcve-1.1-{year}.json.gz"
        local_gzip_path = f"data/feeds/nvdcve-1.1-{year}.json.gz"
        local_json_path = f"data/feeds/extracted/nvdcve-1.1-{year}.json"

        os.makedirs("data/feeds", exist_ok=True)
        os.makedirs("data/feeds/extracted", exist_ok=True)

        # Download the feed
        print(f"Downloading {feed_url}...")
        response = requests.get(feed_url, stream=True)
        if response.status_code == 200:
            with open(local_gzip_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {local_gzip_path}")

            # Extract the feed
            with gzip.open(local_gzip_path, "rb") as gz:
                with open(local_json_path, "wb") as json_file:
                    json_file.write(gz.read())
            print(f"Extracted: {local_json_path}")
        else:
            print(f"Failed to download {feed_url}. Status code: {response.status_code}")

    def populate_database(self, year):
        local_json_path = f"data/feeds/extracted/nvdcve-1.1-{year}.json"
        if not os.path.exists(local_json_path):
            print(f"No JSON file found for {year}. Skipping...")
            return

        with open(local_json_path, "r") as json_file:
            cve_data = json.load(json_file)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for cve_item in cve_data.get("CVE_Items", []):
                cve_id = cve_item["cve"]["CVE_data_meta"]["ID"]
                description = cve_item["cve"]["description"]["description_data"][0]["value"]
                published_date = cve_item["publishedDate"]
                last_modified_date = cve_item["lastModifiedDate"]
                impact = cve_item.get("impact", {}).get("baseMetricV3", {}).get("cvssV3", {}).get("baseSeverity", "Unknown")

                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO cves (cve_id, description, published_date, last_modified_date, impact)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (cve_id, description, published_date, last_modified_date, impact))
                except sqlite3.Error as e:
                    print(f"Database error for {cve_id}: {str(e)}")

            conn.commit()
            conn.close()
            print(f"Database updated for {year}.")

    def run(self):
        self.initialize_database()
        for year in self.feed_years:
            self.download_and_extract_feed(year)
            self.populate_database(year)


if __name__ == "__main__":
    downloader = CVEFeedDownloader()
    downloader.run()
