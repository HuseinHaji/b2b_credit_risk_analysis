import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split


def train_model(feature_data: pd.DataFrame, target_col: str = "has_default") -> dict:
    cols = [c for c in feature_data.columns if c not in ["customer_key", target_col]]
    X = feature_data[cols]
    y = feature_data[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

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
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(path_obj, "wb") as f:
        pickle.dump(model, f)


if __name__ == "__main__":
    raise RuntimeError("Use scripts/run_model_training.py to orchestrate training")
