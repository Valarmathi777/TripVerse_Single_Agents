"""
models/train_model.py
One-off training script. Generates synthetic training examples by running the
deterministic calculator engine across many (destination, days, travelers, style)
combinations, then fits a small regression model that can give an instant rough
cost estimate WITHOUT recomputing the full dataset lookups - used by
services/predictor.py for the /predict-expense endpoint's quick estimate.

Run with:  python models/train_model.py
"""
import sys
import itertools
import random
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.calculator import calculate_full_budget
from utils.helpers import list_destinations

STYLES = ["Budget", "Standard", "Luxury"]


def generate_training_data():
    rows = []
    destinations = list_destinations()
    for destination, days, travelers, style in itertools.product(
        destinations, range(2, 11), [1, 2, 3, 4, 5, 6], STYLES
    ):
        try:
            result = calculate_full_budget(destination, days, travelers, budget=999999, travel_style=style)
        except Exception:
            continue
        rows.append({
            "destination": destination,
            "days": days,
            "travelers": travelers,
            "travel_style": style,
            "total_estimated_cost": result["total_estimated_cost"],
        })
    return pd.DataFrame(rows)


def train():
    df = generate_training_data()
    print(f"Generated {len(df)} synthetic training rows")

    X = df[["destination", "days", "travelers", "travel_style"]]
    y = df["total_estimated_cost"]

    categorical = ["destination", "travel_style"]
    numeric = ["days", "travelers"]

    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ], remainder="passthrough")

    model = Pipeline([
        ("preprocess", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42)),
    ])

    model.fit(X, y)
    score = model.score(X, y)
    print(f"Training R^2 score: {score:.4f}")

    out_path = Path(__file__).resolve().parent / "budget_model.pkl"
    joblib.dump(model, out_path)
    print(f"Saved model to {out_path}")


if __name__ == "__main__":
    train()
