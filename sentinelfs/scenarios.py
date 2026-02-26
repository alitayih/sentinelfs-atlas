import pandas as pd

TEMPLATE_DELTAS = {
    "Export ban": {"export_restriction_sentiment": 0.35, "price_shock": 0.15},
    "Port disruption": {"freight_volatility": 0.35, "price_shock": 0.10},
    "Conflict escalation": {"conflict_intensity": 0.40, "freight_volatility": 0.10},
    "Drought": {"weather_risk": 0.45, "price_shock": 0.10},
}


def apply_scenario(df: pd.DataFrame, iso3: str, commodity: str, template: str, severity: float, duration_days: int) -> pd.DataFrame:
    scoped = df.copy()
    deltas = TEMPLATE_DELTAS[template]
    max_date = scoped["date"].max()
    start_date = max_date - pd.Timedelta(days=duration_days - 1)

    mask = (scoped["iso3"] == iso3) & (scoped["date"] >= start_date)
    if commodity != "All":
        mask &= scoped["commodity"] == commodity

    for col, delta in deltas.items():
        scoped.loc[mask, col] = (scoped.loc[mask, col] + delta * severity).clip(0, 1)

    return scoped
