import os
import json
import requests


def download_cve_data(output_file="data/nvd_local_db.json"):
    """
    Download the latest CVE data feeds and update the local database.
    :param output_file: Path to save the updated CVE data.
    """
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    years = range(2002, 2024)  # Fetch CVEs from 2002 to the current year
    api_key = "YOUR_NVD_API_KEY"  # Replace with your API key if required

    cve_data = {"CVE_Items": []}

    for year in years:
        print(f"Fetching CVE data for {year}...")
        try:
            url = f"{base_url}?pubStartDate={year}-01-01T00:00:00:000 UTC-00:00&pubEndDate={year}-12-31T23:59:59:999 UTC-00:00"
            if api_key:
                url += f"&apiKey={api_key}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            cve_data["CVE_Items"].extend(data.get("vulnerabilities", []))
        except requests.RequestException as e:
            print(f"Error fetching data for {year}: {e}")

    # Save the aggregated CVE data
    with open(output_file, "w") as file:
        json.dump(cve_data, file, indent=4)
    print(f"CVE data updated successfully. Saved to {output_file}")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    download_cve_data()
