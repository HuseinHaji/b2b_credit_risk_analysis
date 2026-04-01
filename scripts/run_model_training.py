from pathlib import Path
import sys

# Ensure local source takes precedence (path may have old pip install location)
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / 'src'))

import pandas as pd
from b2b_credit_risk_analysis.modeling.train import train_model, save_model


def run_model_training(
    feature_path: str = "data/processed/features/customer_feature_dataset.csv",
    model_path: str = "models/rf_default_model.pkl",
):
    project_root = Path(__file__).parent.parent
    feature_file = project_root / feature_path

    if not feature_file.exists():
        raise FileNotFoundError(f"Feature file not found: {feature_file}")

    features = pd.read_csv(feature_file)
    training = train_model(features, target_col="has_default")

    # Persist model
    save_model(training["model"], project_root / model_path)

    print("Model training complete")
    print(f"ROC AUC: {training['metrics']['roc_auc']:.4f}")

    return training


if __name__ == "__main__":
    run_model_training()
