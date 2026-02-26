import numpy as np
import pandas as pd


WEIGHTS = {
    "conflict_intensity": 0.30,
    "freight_volatility": 0.20,
    "export_restriction_sentiment": 0.20,
    "price_shock": 0.15,
    "weather_risk": 0.15,
}


def compute_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["risk_score"] = 100 * sum(out[col] * w for col, w in WEIGHTS.items())
    out["risk_score"] = out["risk_score"].clip(0, 100)
    out["risk_level"] = np.select(
        [out["risk_score"] <= 33, out["risk_score"] <= 66],
        ["Low", "Medium"],
        default="High",
    )
    return out
