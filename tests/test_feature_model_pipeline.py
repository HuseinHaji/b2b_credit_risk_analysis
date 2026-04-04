"""
Tests for Feature Engineering and Model Training Pipeline

This module contains unit tests to ensure the feature engineering
and model training components work correctly and produce expected results.
"""

import pandas as pd

from b2b_credit_risk_analysis.features.panel_features import build_customer_exposure_features
from b2b_credit_risk_analysis.features.risk_features import build_default_label
from b2b_credit_risk_analysis.modeling.train import train_model


def test_build_customer_exposure_features():
    """Test that customer exposure features are calculated correctly."""
    # Create sample exposure data for testing
    df = pd.DataFrame(
        {
            "customer_key": [1, 1, 2],  # Customer 1 has 2 records, customer 2 has 1
            "current_exposure": [100.0, 150.0, 200.0],
            "overdue_exposure": [10.0, 20.0, 5.0],
            "utilization_ratio": [0.2, 0.25, 0.3],
            "snapshot_date_key": [20220131, 20220228, 20220131],
        }
    )

    # Build features
    features = build_customer_exposure_features(df)

    # Check that all expected columns are present
    assert list(features.columns) == [
        "customer_key",
        "total_exposure",
        "total_overdue",
        "avg_utilization",
        "max_overdue",
        "monthly_obs",
        "overdue_rate",
    ]

    # Verify calculations for customer 1 (sum of both records)
    assert features.loc[features.customer_key == 1, "total_exposure"].iloc[0] == 250.0
    assert features.loc[features.customer_key == 1, "total_overdue"].iloc[0] == 30.0

    # Verify calculations for customer 2 (single record)
    assert features.loc[features.customer_key == 2, "total_overdue"].iloc[0] == 5.0


def test_build_default_label():
    """Test that default labels are assigned correctly to customers."""
    # Sample exposure data with 3 customers
    exposure = pd.DataFrame(
        {
            "customer_key": [1, 2, 3],
            "current_exposure": [100, 200, 300],
        }
    )

    # Default events for customers 1 and 3
    defaults = pd.DataFrame(
        {
            "default_event_key": [10, 20],
            "customer_key": [1, 3],
            "default_date": ["2022-03-01", "2022-04-01"],
        }
    )

    # Build labels
    label_df = build_default_label(exposure, defaults)

    # Should have labels for all 3 customers
    assert label_df.shape[0] == 3

    # Customer 1 should have default (has events)
    assert label_df.set_index("customer_key").loc[1, "has_default"] == 1

    # Customer 2 should not have default (no events)
    assert label_df.set_index("customer_key").loc[2, "has_default"] == 0


def test_train_model_smoke():
    """Basic smoke test to ensure model training works without errors."""
    # Create synthetic dataset for testing
    data = pd.DataFrame(
        {
            "customer_key": range(100),
            "total_exposure": list(range(100, 200)),  # 100-199
            "total_overdue": [x % 5 for x in range(100)],  # 0-4 repeating
            "avg_utilization": [0.1 + (x % 10) * 0.01 for x in range(100)],  # 0.1-0.19
            "max_overdue": [x % 6 for x in range(100)],  # 0-5 repeating
            "monthly_obs": [12] * 100,  # All have 12 months
            "has_default": [1 if x % 10 == 0 else 0 for x in range(100)],  # Every 10th customer defaults
        }
    )

    # Train model
    result = train_model(data, target_col="has_default")

    # Basic checks that training completed
    assert "roc_auc" in result["metrics"]
    assert result["metrics"]["roc_auc"] >= 0.5  # Should be better than random
