import pandas as pd


def build_customer_exposure_features(fact_exposure_snapshot: pd.DataFrame) -> pd.DataFrame:
    """Aggregate exposure and overdue trends by customer."""
    df = fact_exposure_snapshot.copy()

    features = (
        df.groupby("customer_key")
        .agg(
            total_exposure=("current_exposure", "sum"),
            total_overdue=("overdue_exposure", "sum"),
            avg_utilization=("utilization_ratio", "mean"),
            max_overdue=("overdue_exposure", "max"),
            monthly_obs=("snapshot_date_key", "nunique"),
        )
        .reset_index()
    )

    features["overdue_rate"] = features["total_overdue"] / features["total_exposure"].replace(0, 1)
    return features
