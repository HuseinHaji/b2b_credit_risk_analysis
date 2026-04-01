import pandas as pd

from b2b_credit_risk_analysis.features.panel_features import build_customer_exposure_features
from b2b_credit_risk_analysis.features.risk_features import build_default_label
from b2b_credit_risk_analysis.modeling.train import train_model


def test_build_customer_exposure_features():
    df = pd.DataFrame(
        {
            "customer_key": [1, 1, 2],
            "current_exposure": [100.0, 150.0, 200.0],
            "overdue_exposure": [10.0, 20.0, 5.0],
            "utilization_ratio": [0.2, 0.25, 0.3],
            "snapshot_date_key": [20220131, 20220228, 20220131],
        }
    )

    features = build_customer_exposure_features(df)

    assert list(features.columns) == [
        "customer_key",
        "total_exposure",
        "total_overdue",
        "avg_utilization",
        "max_overdue",
        "monthly_obs",
        "overdue_rate",
    ]
    assert features.loc[features.customer_key == 1, "total_exposure"].iloc[0] == 250.0
    assert features.loc[features.customer_key == 2, "total_overdue"].iloc[0] == 5.0


def test_build_default_label():
    exposure = pd.DataFrame(
        {
            "customer_key": [1, 2, 3],
            "current_exposure": [100, 200, 300],
        }
    )
    defaults = pd.DataFrame(
        {
            "default_event_key": [10, 20],
            "customer_key": [1, 3],
            "default_date": ["2022-03-01", "2022-04-01"],
        }
    )

    label_df = build_default_label(exposure, defaults)

    assert label_df.shape[0] == 3
    assert label_df.set_index("customer_key").loc[1, "has_default"] == 1
    assert label_df.set_index("customer_key").loc[2, "has_default"] == 0


def test_train_model_smoke():
    data = pd.DataFrame(
        {
            "customer_key": range(100),
            "total_exposure": list(range(100, 200)),
            "total_overdue": [x % 5 for x in range(100)],
            "avg_utilization": [0.1 + (x % 10) * 0.01 for x in range(100)],
            "max_overdue": [x % 6 for x in range(100)],
            "monthly_obs": [12] * 100,
            "has_default": [1 if x % 10 == 0 else 0 for x in range(100)],
        }
    )

    result = train_model(data, target_col="has_default")

    assert "roc_auc" in result["metrics"]
    assert result["metrics"]["roc_auc"] >= 0.5
