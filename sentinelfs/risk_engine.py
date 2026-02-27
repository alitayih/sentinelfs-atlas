import pandas as pd

WEIGHTS = {
    "conflict_intensity": 0.30,
    "freight_volatility": 0.20,
    "export_restriction_sentiment": 0.20,
    "price_shock": 0.15,
    "weather_risk": 0.15,
}

DRIVER_COLS = list(WEIGHTS.keys())


def compute_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # drivers لازم تكون موجودة
    out["risk_score"] = 100 * (
        0.30 * out["conflict_intensity"]
        + 0.20 * out["freight_volatility"]
        + 0.20 * out["export_restriction_sentiment"]
        + 0.15 * out["price_shock"]
        + 0.15 * out["weather_risk"]
    )
    out["risk_score"] = out["risk_score"].clip(0, 100).round(1)

    out["risk_level"] = np.select(
        [out["risk_score"] <= 33, out["risk_score"] <= 66, out["risk_score"] > 66],
        ["Low", "Medium", "High"],
        default="Medium",
    )
    return out
