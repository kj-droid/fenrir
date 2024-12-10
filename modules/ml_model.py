import pandas as pd
import os
import json
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


class MLModel:
    def __init__(self, model_path="models/vulnerability_predictor.pkl", output_dir="reports/output"):
        """
        Initialize the MLModel.
        :param model_path: Path to save or load the trained model.
        :param output_dir: Directory to save predictions.
        """
        self.model_path = model_path
        self.output_dir = output_dir
        self.logger = logging.getLogger("MLModel")
        logging.basicConfig(level=logging.INFO)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.model = None

    def load_data(self, data_file="data/vulnerability_data.csv"):
        """
        Load historical scan data for training or prediction.
        :param data_file: Path to the CSV file containing the data.
        :return: Pandas DataFrame of the data.
        """
        try:
            self.logger.info(f"Loading data from {data_file}...")
            data = pd.read_csv(data_file)
            return data
        except FileNotFoundError:
            self.logger.error(f"Data file not found: {data_file}")
            return None

    def train_model(self, data_file="data/vulnerability_data.csv"):
        """
        Train the machine learning model using historical data.
        :param data_file: Path to the CSV file containing the data.
        """
        data = self.load_data(data_file)
        if data is None:
            return

        # Assume the data contains 'features' and 'labels' columns
        X = data.drop(columns=["label"])
        y = data["label"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.logger.info("Training the model...")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        self.logger.info(f"Model accuracy: {accuracy_score(y_test, y_pred)}")
        self.logger.info(f"Classification report:\n{classification_report(y_test, y_pred)}")

        # Save the trained model
        joblib.dump(model, self.model_path)
        self.logger.info(f"Model saved to {self.model_path}")

        self.model = model

    def load_model(self):
        """
        Load a pre-trained machine learning model.
        """
        try:
            self.logger.info(f"Loading model from {self.model_path}...")
            self.model = joblib.load(self.model_path)
        except FileNotFoundError:
            self.logger.error(f"Model file not found: {self.model_path}")
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")

    def predict_vulnerabilities(self, feature_data):
        """
        Predict vulnerabilities based on input features.
        :param feature_data: DataFrame containing features for prediction.
        :return: Predicted labels.
        """
        if self.model is None:
            self.logger.error("Model not loaded. Load or train the model before predicting.")
            return None

        self.logger.info("Predicting vulnerabilities...")
        predictions = self.model.predict(feature_data)
        return predictions

    def save_predictions(self, predictions, output_file="predictions.json"):
        """
        Save predictions to a JSON file.
        :param predictions: List of predicted labels.
        :param output_file: Name of the output file.
        """
        file_path = os.path.join(self.output_dir, output_file)
        try:
            with open(file_path, "w") as file:
                json.dump({"predictions": predictions}, file, indent=4)
            self.logger.info(f"Predictions saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving predictions: {e}")


if __name__ == "__main__":
    # Example usage
    ml_model = MLModel()

    # Train the model
    ml_model.train_model()

    # Load the trained model
    ml_model.load_model()

    # Predict vulnerabilities
    feature_data = pd.DataFrame([
        {"feature1": 0.5, "feature2": 0.3, "feature3": 0.8},
        {"feature1": 0.1, "feature2": 0.7, "feature3": 0.2}
    ])
    predictions = ml_model.predict_vulnerabilities(feature_data)

    # Save predictions
    ml_model.save_predictions(predictions)

    # Print predictions
    print("Predictions:")
    print(predictions)
