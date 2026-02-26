import numpy as np
import pandas as pd


def format_risk_metrics(country_risk: pd.DataFrame) -> tuple[float, float]:
    high_pct = (country_risk["risk_level"].eq("High").mean() * 100) if len(country_risk) else 0.0
    avg_score = country_risk["risk_score"].mean() if len(country_risk) else 0.0
    return high_pct, avg_score


def sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))
