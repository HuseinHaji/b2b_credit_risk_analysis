"""
Model Training Script for B2B Credit Risk Prediction

This script trains a machine learning model to predict customer default risk
using the engineered features. It uses a Random Forest classifier and provides
comprehensive evaluation metrics.
"""

from pathlib import Path
import sys

# Add source directory to path for imports
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / 'src'))

import pandas as pd
from b2b_credit_risk_analysis.modeling.train import train_model, save_model


def run_model_training(
    feature_path: str = "data/processed/features/customer_feature_dataset.csv",
    model_path: str = "models/rf_default_model.pkl",
):
    """
    Train and save a credit risk prediction model.

    This function:
    1. Loads the feature dataset
    2. Trains a Random Forest model using the training module
    3. Saves the trained model to disk
    4. Prints key performance metrics

    Args:
        feature_path: Path to the feature dataset CSV
        model_path: Path where to save the trained model

    Returns:
        Training results dictionary containing model and metrics
    """
    project_root = Path(__file__).parent.parent
    feature_file = project_root / feature_path

    # Check if feature file exists
    if not feature_file.exists():
        raise FileNotFoundError(f"Feature file not found: {feature_file}")

    # Load the prepared feature dataset
    features = pd.read_csv(feature_file)

    # Train the model using our custom training function
    training = train_model(features, target_col="has_default")

    # Save the trained model for later use
    save_model(training["model"], project_root / model_path)

    # Report results
    print("Model training complete")
    print(f"ROC AUC: {training['metrics']['roc_auc']:.4f}")

    return training


if __name__ == "__main__":
    # Run model training with default settings
    run_model_training()
