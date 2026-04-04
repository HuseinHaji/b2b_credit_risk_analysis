"""
Customer-Level Feature Engineering for Credit Risk

This module creates aggregated features from customer exposure snapshots.
These features capture the credit behavior and risk profile of each customer.
"""

import pandas as pd


def build_customer_exposure_features(fact_exposure_snapshot: pd.DataFrame) -> pd.DataFrame:
    """
    Build customer-level features from exposure snapshot data.

    This function aggregates transactional exposure data into meaningful
    customer-level risk indicators that can be used for credit scoring.

    Args:
        fact_exposure_snapshot: DataFrame with customer exposure snapshots

    Returns:
        DataFrame with one row per customer containing aggregated features
    """
    df = fact_exposure_snapshot.copy()

    # Aggregate features by customer
    # These capture different aspects of credit risk:
    # - Total exposure: overall credit usage
    # - Total overdue: accumulated payment delays
    # - Average utilization: typical credit usage ratio
    # - Max overdue: worst payment delay
    # - Monthly observations: data completeness indicator
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

    # Calculate overdue rate as a risk indicator
    # Avoid division by zero by replacing 0 exposure with 1
    features["overdue_rate"] = features["total_overdue"] / features["total_exposure"].replace(0, 1)

    return features
