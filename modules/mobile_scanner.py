import os
import requests
import logging
import json


class MobileScanner:
    def __init__(self, target_url, output_dir="reports/output"):
        """
        Initialize the MobileScanner.
        :param target_url: Base URL of the mobile application's backend API.
        :param output_dir: Directory to save scan results.
        """
        self.target_url = target_url.rstrip("/")
        self.output_dir = output_dir
        self.logger = logging.getLogger("MobileScanner")
        logging.basicConfig(level=logging.INFO)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def check_api_endpoints(self, api_endpoints):
        """
        Scan mobile application API endpoints for issues.
        :param api_endpoints: List of API endpoints to check.
        :return: List of endpoints with potential issues.
        """
        self.logger.info("Checking API endpoints...")
        issues = []
        for endpoint in api_endpoints:
            url = f"{self.target_url}/{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.logger.info(f"Endpoint {url} is accessible.")
                    if "debug" in response.text.lower() or "error" in response.text.lower():
                        issues.append({
                            "endpoint": url,
                            "issue": "Potential debug or error information leakage."
                        })
            except Exception as e:
                self.logger.warning(f"Error accessing {url}: {e}")
        return issues

    def analyze_permissions(self, permissions_file="data/mobile_permissions.json"):
        """
        Analyze permissions for potential security risks.
        :param permissions_file: Path to the JSON file containing permission definitions.
        :return: List of risky permissions.
        """
        self.logger.info("Analyzing permissions...")
        risky_permissions = []
        try:
            with open(permissions_file, "r") as file:
                permissions_data = json.load(file)
                for permission, description in permissions_data.items():
                    if "risky" in description.lower():
                        self.logger.warning(f"Permission {permission} flagged as risky.")
                        risky_permissions.append({
                            "permission": permission,
                            "description": description
                        })
        except FileNotFoundError:
            self.logger.error(f"Permissions file not found: {permissions_file}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding permissions file: {e}")
        return risky_permissions

    def detect_sensitive_data(self, file_paths):
        """
        Scan local files or app data for sensitive information.
        :param file_paths: List of file paths to scan.
        :return: List of files with detected sensitive data.
        """
        self.logger.info("Scanning for sensitive data...")
        sensitive_files = []
        keywords = ["password", "secret", "key", "token"]
        for file_path in file_paths:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    if any(keyword in content.lower() for keyword in keywords):
                        self.logger.warning(f"Sensitive data detected in {file_path}")
                        sensitive_files.append(file_path)
            except FileNotFoundError:
                self.logger.warning(f"File not found: {file_path}")
            except Exception as e:
                self.logger.error(f"Error reading file {file_path}: {e}")
        return sensitive_files

    def save_results(self, api_issues, risky_permissions, sensitive_files, output_file="mobile_scan_results.json"):
        """
        Save mobile scan results to a JSON file.
        :param api_issues: List of API endpoint issues.
        :param risky_permissions: List of risky permissions.
        :param sensitive_files: List of files with sensitive data.
        :param output_file: Name of the output file.
        """
        file_path = os.path.join(self.output_dir, output_file)
        results = {
            "target": self.target_url,
            "api_issues": api_issues,
            "risky_permissions": risky_permissions,
            "sensitive_files": sensitive_files,
        }
        try:
            with open(file_path, "w") as file:
                json.dump(results, file, indent=4)
            self.logger.info(f"Mobile scan results saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")


if __name__ == "__main__":
    # Example usage
    target = "https://example.com/api"
    scanner = MobileScanner(target_url=target)

    # Check API endpoints
    api_endpoints = ["login", "register", "debug", "admin"]
    api_issues = scanner.check_api_endpoints(api_endpoints)

    # Analyze permissions
    risky_permissions = scanner.analyze_permissions()

    # Detect sensitive data
    file_paths = ["data/user_data.txt", "data/config.json"]
    sensitive_files = scanner.detect_sensitive_data(file_paths)

    # Save results
    scanner.save_results(api_issues, risky_permissions, sensitive_files)

    # Print results
    print("\nAPI Issues:")
    print(api_issues)
    print("\nRisky Permissions:")
    print(risky_permissions)
    print("\nSensitive Files:")
    print(sensitive_files)
