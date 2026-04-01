import pandas as pd


def build_default_label(fact_exposure_snapshot: pd.DataFrame, fact_default_event: pd.DataFrame) -> pd.DataFrame:
    """Build a per-customer default label using events in default table."""
    defaults = fact_default_event.copy()

    default_label = (
        defaults.groupby("customer_key")
        .agg(has_default=("default_event_key", "count"))
        .reset_index()
    )
    default_label["has_default"] = (default_label["has_default"] > 0).astype(int)

    merged = fact_exposure_snapshot["customer_key"].drop_duplicates().to_frame()
    merged = merged.merge(default_label, on="customer_key", how="left").fillna(0)
    merged["has_default"] = merged["has_default"].astype(int)
    return merged
