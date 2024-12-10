
import os

def generate_test_data(output_path="data/test_data.json"):
    data = {"test": "This is test data for Fenrir modules."}
    with open(output_path, "w") as f:
        f.write(str(data))
    print(f"Test data generated at {output_path}")

if __name__ == "__main__":
    generate_test_data()
