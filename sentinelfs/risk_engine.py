# sentinelfs/risk_engine.py
from __future__ import annotations

import numpy as np
import pandas as pd


WEIGHTS = {
    "conflict_intensity": 0.28,
    "freight_volatility": 0.18,
    "export_restriction_sentiment": 0.18,
    "price_shock": 0.16,
    "weather_risk": 0.20,
}


def compute_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes weighted risk_score (0-100) and risk_level.
    Expects the signal columns to exist in df (or will fill missing with 0).
    """
    out = df.copy()

    # Ensure columns exist
    for col in WEIGHTS.keys():
        if col not in out.columns:
            out[col] = 0.0

    out["risk_score"] = 0.0
    for col, w in WEIGHTS.items():
        out["risk_score"] += out[col].astype(float) * w

    out["risk_score"] = out["risk_score"].clip(0, 100).round(1)

    out["risk_level"] = np.select(
        [out["risk_score"] <= 33, out["risk_score"] <= 66, out["risk_score"] > 66],
        ["Low", "Medium", "High"],
        default="Medium",
    )

    return out
