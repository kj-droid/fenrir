import pandas as pd
import random
import os


def generate_test_data(output_file="data/vulnerability_data.csv", rows=1000):
    """
    Generate synthetic test data for machine learning models.
    :param output_file: Path to save the generated CSV file.
    :param rows: Number of rows to generate.
    """
    data = []
    for _ in range(rows):
        feature1 = round(random.uniform(0, 1), 2)
        feature2 = round(random.uniform(0, 1), 2)
        feature3 = round(random.uniform(0, 1), 2)
        label = 1 if feature1 + feature2 + feature3 > 1.5 else 0
        data.append([feature1, feature2, feature3, label])

    df = pd.DataFrame(data, columns=["feature1", "feature2", "feature3", "label"])
    os.makedirs("data", exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Test data generated and saved to {output_file}")


if __name__ == "__main__":
    generate_test_data()
