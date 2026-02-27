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
    """
    Adds:
      - risk_score (0..100, rounded 1)
      - risk_level (Low/Medium/High)
    Assumes driver columns exist in df (or fills missing with 0).
    """
    out = df.copy()

    for c in DRIVER_COLS:
        if c not in out.columns:
            out[c] = 0.0
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0).clip(0, 1)

    score = 0.0
    for c, w in WEIGHTS.items():
        score = score + w * out[c]

    out["risk_score"] = (100.0 * score).clip(0, 100).round(1)

    def _level(x: float) -> str:
        if x <= 33:
            return "Low"
        if x <= 66:
            return "Medium"
        return "High"

    out["risk_level"] = out["risk_score"].apply(_level)
    return out
