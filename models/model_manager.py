import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os


class ModelManager:
    def __init__(self, model_path="models/vulnerability_predictor.pkl"):
        """
        Initialize the ModelManager.
        :param model_path: Path to the saved model file.
        """
        self.model_path = model_path
        self.model = None

    def load_model(self):
        """
        Load the pre-trained machine learning model.
        """
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print(f"Model loaded from {self.model_path}")
        else:
            print(f"Model file not found at {self.model_path}. Train a new model first.")

    def train_model(self, data_file="data/vulnerability_data.csv"):
        """
        Train a new machine learning model using historical data.
        :param data_file: Path to the CSV file containing training data.
        """
        if not os.path.exists(data_file):
            print(f"Data file not found: {data_file}")
            return

        data = pd.read_csv(data_file)

        # Assume features are all columns except the last, and the last column is the label
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train a Random Forest model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        # Evaluate the model
        y_pred = self.model.predict(X_test)
        print("Training completed.")
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("Classification Report:\n", classification_report(y_test, y_pred))

        # Save the trained model
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")

    def predict(self, features):
        """
        Predict vulnerabilities using the trained model.
        :param features: DataFrame containing features for prediction.
        :return: Predictions (0 or 1 for each instance).
        """
        if self.model is None:
            print("Model not loaded. Load or train a model before predicting.")
            return None

        predictions = self.model.predict(features)
        return predictions


if __name__ == "__main__":
    # Example usage
    manager = ModelManager()

    # Train a new model
    manager.train_model(data_file="data/vulnerability_data.csv")

    # Load the trained model
    manager.load_model()

    # Predict vulnerabilities
    test_features = pd.DataFrame([
        {"feature1": 0.5, "feature2": 0.3, "feature3": 0.8},
        {"feature1": 0.1, "feature2": 0.7, "feature3": 0.2}
    ])
    predictions = manager.predict(test_features)
    print("Predictions:", predictions)
