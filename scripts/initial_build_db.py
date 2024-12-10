import os
import json
import requests
import gzip


def download_nvd_feeds(feed_directory="data/feeds"):
    """
    Download NVD JSON feeds for all years and save them to the specified directory.
    :param feed_directory: Directory to save downloaded feed files.
    """
    os.makedirs(feed_directory, exist_ok=True)
    base_url = "https://nvd.nist.gov/feeds/json/cve/1.1/"
    years = range(2002, 2024)  # Modify as needed to include the latest year

    for year in years:
        feed_filename = f"nvdcve-1.1-{year}.json.gz"
        feed_url = f"{base_url}{feed_filename}"
        local_file_path = os.path.join(feed_directory, feed_filename)

        if os.path.exists(local_file_path):
            print(f"Feed for {year} already downloaded: {local_file_path}")
            continue

        print(f"Downloading feed for {year}: {feed_url}")
        try:
            response = requests.get(feed_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(local_file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)

            print(f"Successfully downloaded: {local_file_path}")
        except requests.RequestException as e:
            print(f"Error downloading feed for {year}: {e}")


def extract_feed_files(feed_directory="data/feeds", extracted_directory="data/feeds/extracted"):
    """
    Extract all gzip-compressed JSON files in the feed directory.
    :param feed_directory: Directory containing downloaded .gz files.
    :param extracted_directory: Directory to save extracted JSON files.
    """
    os.makedirs(extracted_directory, exist_ok=True)

    for filename in os.listdir(feed_directory):
        if filename.endswith(".json.gz"):
            input_path = os.path.join(feed_directory, filename)
            output_path = os.path.join(extracted_directory, filename.replace(".json.gz", ".json"))

            if os.path.exists(output_path):
                print(f"Feed already extracted: {output_path}")
                continue

            print(f"Extracting {input_path} to {output_path}")
            try:
                with gzip.open(input_path, "rt", encoding="utf-8") as gz_file:
                    with open(output_path, "w") as json_file:
                        json_file.write(gz_file.read())
                print(f"Successfully extracted: {output_path}")
            except Exception as e:
                print(f"Error extracting {input_path}: {e}")


def build_initial_db(extracted_directory="data/feeds/extracted", output_file="data/nvd_local_db.json"):
    """
    Build the initial local CVE database from extracted JSON feed files.
    :param extracted_directory: Directory containing extracted JSON files.
    :param output_file: Path to save the consolidated local database.
    """
    if not os.path.exists(extracted_directory):
        print(f"Extracted feed directory '{extracted_directory}' does not exist.")
        return

    cve_data = {"CVE_Items": []}

    for filename in os.listdir(extracted_directory):
        file_path = os.path.join(extracted_directory, filename)
        if filename.endswith(".json"):
            print(f"Processing file: {file_path}")
            try:
                with open(file_path, "r") as file:
                    data = json.load(file)
                    cve_data["CVE_Items"].extend(data.get("CVE_Items", []))
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    # Save the aggregated CVE data
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as file:
        json.dump(cve_data, file, indent=4)
    print(f"Initial CVE database built and saved to {output_file}")


if __name__ == "__main__":
    # Define directories
    feed_dir = "data/feeds"
    extracted_dir = "data/feeds/extracted"
    output_db = "data/nvd_local_db.json"

    # Step 1: Download feeds
    print("Step 1: Downloading feeds...")
    download_nvd_feeds(feed_dir)

    # Step 2: Extract feeds
    print("\nStep 2: Extracting feeds...")
    extract_feed_files(feed_dir, extracted_dir)

    # Step 3: Build initial database
    print("\nStep 3: Building initial CVE database...")
    build_initial_db(extracted_dir, output_db)
