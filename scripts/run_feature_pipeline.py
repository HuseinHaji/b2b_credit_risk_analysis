from pathlib import Path
import sys

# Ensure local source takes precedence (path may have old pip install location)
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / 'src'))

import pandas as pd
from b2b_credit_risk_analysis.features.panel_features import build_customer_exposure_features
from b2b_credit_risk_analysis.features.risk_features import build_default_label


def run_feature_pipeline(input_dir: str = "data/processed/phase2", output_dir: str = "data/processed/features"):
    project_root = Path(__file__).parent.parent
    input_path = project_root / input_dir
    output_path = project_root / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    fact_exposure_snapshot = pd.read_csv(input_path / "fact_exposure_snapshot.csv")
    fact_default_event = pd.read_csv(input_path / "fact_default_event.csv")

    customer_features = build_customer_exposure_features(fact_exposure_snapshot)
    target_label = build_default_label(fact_exposure_snapshot, fact_default_event)

    dataset = customer_features.merge(target_label, on="customer_key", how="left")
    dataset["has_default"] = dataset["has_default"].fillna(0).astype(int)

    dataset_path = output_path / "customer_feature_dataset.csv"
    dataset.to_csv(dataset_path, index=False)

    print(f"Saved features: {dataset.shape} -> {dataset_path}")
    return dataset


if __name__ == "__main__":
    run_feature_pipeline()
