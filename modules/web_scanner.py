import requests
from concurrent.futures import ThreadPoolExecutor
import logging
import os


class WebScanner:
    def __init__(self, target_url, timeout=5, output_dir="reports/output"):
        """
        Initialize the WebScanner.
        :param target_url: Base URL of the target web application.
        :param timeout: Timeout for HTTP requests in seconds.
        :param output_dir: Directory to save scan results.
        """
        self.target_url = target_url.rstrip("/")
        self.timeout = timeout
        self.output_dir = output_dir
        self.logger = logging.getLogger("WebScanner")
        logging.basicConfig(level=logging.INFO)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def check_headers(self):
        """
        Check HTTP headers for potential security issues.
        :return: Dictionary of headers with potential issues highlighted.
        """
        self.logger.info("Checking HTTP headers...")
        issues = {}
        try:
            response = requests.head(self.target_url, timeout=self.timeout)
            headers = response.headers

            # Check common security headers
            if "X-Content-Type-Options" not in headers:
                issues["X-Content-Type-Options"] = "Missing"
            if "X-Frame-Options" not in headers:
                issues["X-Frame-Options"] = "Missing"
            if "Content-Security-Policy" not in headers:
                issues["Content-Security-Policy"] = "Missing"
            if "Strict-Transport-Security" not in headers:
                issues["Strict-Transport-Security"] = "Missing"

            self.logger.info(f"Headers checked: {headers}")
            return {"headers": headers, "issues": issues}
        except Exception as e:
            self.logger.error(f"Error checking headers: {e}")
            return {"headers": {}, "issues": {"Error": str(e)}}

    def brute_force_directories(self, wordlist="data/wordlists/directories.txt", max_threads=10):
        """
        Perform directory brute-forcing to discover hidden resources.
        :param wordlist: Path to the wordlist file.
        :param max_threads: Maximum number of concurrent threads for brute-forcing.
        :return: List of discovered directories.
        """
        self.logger.info(f"Starting directory brute-forcing on {self.target_url}...")
        discovered = []

        def check_directory(directory):
            url = f"{self.target_url}/{directory}"
            try:
                response = requests.head(url, timeout=self.timeout)
                if response.status_code == 200:
                    self.logger.info(f"Discovered: {url}")
                    discovered.append(url)
            except Exception as e:
                self.logger.warning(f"Error checking {url}: {e}")

        try:
            with open(wordlist, "r") as file:
                directories = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            self.logger.error(f"Wordlist not found: {wordlist}")
            return []

        with ThreadPoolExecutor(max_threads) as executor:
            executor.map(check_directory, directories)

        self.logger.info("Directory brute-forcing completed.")
        return discovered

    def save_results(self, headers, discovered_directories, output_file="web_scan_results.json"):
        """
        Save web scan results to a JSON file.
        :param headers: HTTP headers and potential issues.
        :param discovered_directories: List of discovered directories.
        :param output_file: Path to the output file.
        """
        file_path = os.path.join(self.output_dir, output_file)
        results = {
            "target": self.target_url,
            "headers": headers,
            "discovered_directories": discovered_directories,
        }
        try:
            import json
            with open(file_path, "w") as file:
                json.dump(results, file, indent=4)
            self.logger.info(f"Web scan results saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")


if __name__ == "__main__":
    # Example usage
    target = "http://example.com"
    scanner = WebScanner(target_url=target)

    # Check headers
    headers = scanner.check_headers()
    print("\nHTTP Headers and Issues:")
    print(headers)

    # Perform directory brute-forcing
    discovered_dirs = scanner.brute_force_directories()
    print("\nDiscovered Directories:")
    for directory in discovered_dirs:
        print(directory)

    # Save results
    scanner.save_results(headers, discovered_dirs)
