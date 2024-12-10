import json
import os
import logging


class DatabaseManager:
    def __init__(self, db_path="data/nvd_local_db.json"):
        """
        Initialize the DatabaseManager.
        :param db_path: Path to the local database JSON file.
        """
        self.db_path = db_path
        self.logger = logging.getLogger("DatabaseManager")
        logging.basicConfig(level=logging.INFO)

        # Ensure the database file exists
        if not os.path.exists(db_path):
            self.logger.info("Database file not found. Initializing a new database.")
            self._initialize_database()

    def _initialize_database(self):
        """
        Initialize an empty database.
        """
        try:
            with open(self.db_path, "w") as file:
                json.dump({"CVE_Items": []}, file, indent=4)
            self.logger.info("New database initialized.")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")

    def add_vulnerabilities(self, vulnerabilities):
        """
        Add new vulnerabilities to the database.
        :param vulnerabilities: List of vulnerabilities to add.
        """
        try:
            with open(self.db_path, "r") as file:
                db_data = json.load(file)

            db_data["CVE_Items"].extend(vulnerabilities)

            with open(self.db_path, "w") as file:
                json.dump(db_data, file, indent=4)

            self.logger.info(f"Added {len(vulnerabilities)} vulnerabilities to the database.")
        except Exception as e:
            self.logger.error(f"Error adding vulnerabilities: {e}")

    def query_vulnerabilities(self, software_name, severity_threshold="LOW"):
        """
        Query vulnerabilities for a specific software.
        :param software_name: Software name to search for vulnerabilities.
        :param severity_threshold: Minimum severity level (LOW, MEDIUM, HIGH, CRITICAL).
        :return: List of matching vulnerabilities.
        """
        severity_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

        try:
            with open(self.db_path, "r") as file:
                db_data = json.load(file)

            matches = []
            for cve in db_data.get("CVE_Items", []):
                description = cve.get("cve", {}).get("description", {}).get("description_data", [{}])[0].get("value", "")
                severity = cve.get("impact", {}).get("baseMetricV3", {}).get("cvssV3", {}).get("baseSeverity", "LOW")
                severity_rank = severity_levels.get(severity.upper(), 0)

                if software_name.lower() in description.lower() and severity_rank >= severity_levels.get(severity_threshold.upper(), 0):
                    matches.append({
                        "id": cve.get("cve", {}).get("CVE_data_meta", {}).get("ID", ""),
                        "description": description,
                        "severity": severity,
                        "references": [ref.get("url", "") for ref in cve.get("cve", {}).get("references", {}).get("reference_data", [])]
                    })

            self.logger.info(f"Found {len(matches)} vulnerabilities matching query.")
            return matches
        except Exception as e:
            self.logger.error(f"Error querying vulnerabilities: {e}")
            return []

    def check_for_updates(self, new_data_path):
        """
        Check if new data needs to be added to the database.
        :param new_data_path: Path to a new JSON file containing CVEs.
        """
        try:
            if not os.path.exists(new_data_path):
                self.logger.error(f"New data file not found: {new_data_path}")
                return

            with open(new_data_path, "r") as file:
                new_data = json.load(file)

            with open(self.db_path, "r") as file:
                current_data = json.load(file)

            current_cve_ids = {cve.get("cve", {}).get("CVE_data_meta", {}).get("ID", "") for cve in current_data.get("CVE_Items", [])}
            new_cves = [cve for cve in new_data.get("CVE_Items", []) if cve.get("cve", {}).get("CVE_data_meta", {}).get("ID", "") not in current_cve_ids]

            if new_cves:
                self.add_vulnerabilities(new_cves)
                self.logger.info(f"Database updated with {len(new_cves)} new vulnerabilities.")
            else:
                self.logger.info("Database is already up-to-date.")
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")

    def update_seclists(local_path="data/wordlists/"):
        """
        Update SecLists to ensure the latest wordlists are available.
        :param local_path: Local path to save the SecLists directory.
        """
        try:
            import git
            if os.path.exists(local_path):
                repo = git.Repo(local_path)
                repo.remote().pull()
            else:
                git.Repo.clone_from("https://github.com/danielmiessler/SecLists.git", local_path)
            logger.info("SecLists updated successfully.")
        except Exception as e:
            logger.error(f"Failed to update SecLists: {e}")



if __name__ == "__main__":
    # Example usage
    db_manager = DatabaseManager()

    # Example: Add new vulnerabilities
    new_vulnerabilities = [
        {
            "cve": {
                "CVE_data_meta": {"ID": "CVE-2023-12345"},
                "description": {
                    "description_data": [{"value": "Example vulnerability in Apache HTTP Server."}]
                },
                "references": {"reference_data": [{"url": "https://example.com/cve-2023-12345"}]}
            },
            "impact": {
                "baseMetricV3": {
                    "cvssV3": {"baseSeverity": "HIGH"}
                }
            }
        }
    ]
    db_manager.add_vulnerabilities(new_vulnerabilities)

    # Example: Query vulnerabilities
    results = db_manager.query_vulnerabilities("Apache", severity_threshold="HIGH")
    for vuln in results:
        print(f"CVE ID: {vuln['id']}")
        print(f"Description: {vuln['description']}")
        print(f"Severity: {vuln['severity']}")
        print(f"References: {', '.join(vuln['references'])}\n")

    # Example: Check for updates
    db_manager.check_for_updates("data/new_cve_data.json")
