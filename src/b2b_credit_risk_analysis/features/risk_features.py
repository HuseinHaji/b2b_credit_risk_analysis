"""
Target Label Creation for Credit Risk Modeling

This module creates binary default labels from historical default events.
The labels indicate whether a customer has experienced any default events.
"""

import pandas as pd


def build_default_label(fact_exposure_snapshot: pd.DataFrame, fact_default_event: pd.DataFrame) -> pd.DataFrame:
    """
    Create binary default labels for each customer.

    This function determines which customers have had default events
    by checking the default event table. A customer is labeled as
    having defaulted if they have any default events in the history.

    Args:
        fact_exposure_snapshot: Customer exposure data (used to get all customers)
        fact_default_event: Historical default events

    Returns:
        DataFrame with customer_key and has_default (0/1) columns
    """
    defaults = fact_default_event.copy()

    # Count default events per customer
    default_label = (
        defaults.groupby("customer_key")
        .agg(has_default=("default_event_key", "count"))
        .reset_index()
    )

    # Convert count to binary label (any defaults = 1)
    default_label["has_default"] = (default_label["has_default"] > 0).astype(int)

    # Get all unique customers from exposure data
    merged = fact_exposure_snapshot["customer_key"].drop_duplicates().to_frame()

    # Left join to include customers with no defaults (will be NaN, then filled with 0)
    merged = merged.merge(default_label, on="customer_key", how="left").fillna(0)
    merged["has_default"] = merged["has_default"].astype(int)

    return merged
