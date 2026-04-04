"""
Credit Risk Model Training Module

This module contains functions for training and evaluating
machine learning models for credit risk prediction.
"""

import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split


def train_model(feature_data: pd.DataFrame, target_col: str = "has_default") -> dict:
    """
    Train a Random Forest model for credit risk prediction.

    This function handles the complete model training pipeline:
    - Feature selection (excluding ID and target columns)
    - Train/test split with stratification
    - Model training with optimized parameters
    - Performance evaluation

    Args:
        feature_data: DataFrame containing features and target
        target_col: Name of the target column

    Returns:
        Dictionary containing trained model, metrics, and evaluation data
    """
    # Select features, excluding customer ID and target
    cols = [c for c in feature_data.columns if c not in ["customer_key", target_col]]
    X = feature_data[cols]
    y = feature_data[target_col]

    # Split data maintaining class balance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # Train Random Forest with tuned parameters
    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # Generate predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Calculate comprehensive metrics
    metrics = {
        "classification_report": classification_report(y_test, y_pred, digits=4, output_dict=True),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }

    return {
        "model": model,
        "metrics": metrics,
        "features": cols,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
        "y_proba": y_proba,
    }


def save_model(model, path: str):
    """
    Save a trained model to disk using pickle.

    Args:
        model: Trained scikit-learn model
        path: File path where to save the model
    """
    path_obj = Path(path)
    # Ensure the directory exists
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Save the model
    with open(path_obj, "wb") as f:
        pickle.dump(model, f)


if __name__ == "__main__":
    # Prevent accidental execution - use the script instead
    raise RuntimeError("Use scripts/run_model_training.py to orchestrate training")
