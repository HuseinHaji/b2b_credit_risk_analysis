"""
Feature Engineering Pipeline for B2B Credit Risk

This script builds customer-level features from the data warehouse
for use in credit risk prediction models. It aggregates transactional
data into meaningful risk indicators.
"""

from pathlib import Path
import sys

# Add the source directory to the path so we can import our modules
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / 'src'))

import pandas as pd
from b2b_credit_risk_analysis.features.panel_features import build_customer_exposure_features
from b2b_credit_risk_analysis.features.risk_features import build_default_label


def run_feature_pipeline(input_dir: str = "data/processed/phase2", output_dir: str = "data/processed/features"):
    """
    Main feature engineering pipeline.

    This function:
    1. Loads the exposure snapshot and default event data
    2. Builds customer-level features from exposure data
    3. Creates default labels from historical default events
    4. Merges features and labels into a modeling dataset
    5. Saves the final dataset

    Args:
        input_dir: Directory containing phase2 processed data
        output_dir: Directory to save the feature dataset

    Returns:
        Final feature dataframe with target labels
    """
    project_root = Path(__file__).parent.parent
    input_path = project_root / input_dir
    output_path = project_root / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Load the core datasets from the warehouse
    fact_exposure_snapshot = pd.read_csv(input_path / "fact_exposure_snapshot.csv")
    fact_default_event = pd.read_csv(input_path / "fact_default_event.csv")

    # Build features: aggregate exposure metrics per customer
    customer_features = build_customer_exposure_features(fact_exposure_snapshot)

    # Build labels: determine which customers have defaulted
    target_label = build_default_label(fact_exposure_snapshot, fact_default_event)

    # Combine features and labels
    dataset = customer_features.merge(target_label, on="customer_key", how="left")

    # Handle missing labels (customers with no defaults)
    dataset["has_default"] = dataset["has_default"].fillna(0).astype(int)

    # Save the final dataset
    dataset_path = output_path / "customer_feature_dataset.csv"
    dataset.to_csv(dataset_path, index=False)

    print(f"Saved features: {dataset.shape} -> {dataset_path}")
    return dataset


if __name__ == "__main__":
    # Run the feature engineering pipeline with default settings
    run_feature_pipeline()
