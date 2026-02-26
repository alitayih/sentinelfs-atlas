import streamlit as st

from sentinelfs.config import APP_TITLE

st.set_page_config(page_title=f"{APP_TITLE} | Help", page_icon="📘", layout="wide")
st.title("Help & User Manual")

st.markdown(
    """
## What this app does
SentinelFS Atlas is a proof-of-concept country-level food system risk explorer built on synthetic data.

## Pages
1. **Map Home**: Country choropleth by ISO3, KPIs, top risk table, and advanced analytics.
2. **Country Focus**: Deep dive into one country's risk and risk-driver trends plus spike events.
3. **Scenarios**: Apply scenario templates (Export ban, Port disruption, Conflict escalation, Drought).
4. **Action Tracking**: Store and track mitigation actions in Neon Postgres.
5. **Help/User Manual**: This guide.

## Risk formula
`risk_score = 100 * (0.30*conflict_intensity + 0.20*freight_volatility + 0.20*export_restriction_sentiment + 0.15*price_shock + 0.15*weather_risk)`

Scores are clamped to 0..100.
Risk levels:
- Low: <=33
- Medium: <=66
- High: >66

## Filters and windows
- Window supports last 30 or 90 days.
- Commodity supports All/Wheat/Rice/Corn. All aggregates across commodities.

## Scenarios
Template deltas are applied to target-country drivers with configurable severity and duration (7/14/30 days), then risk is recomputed.

## Actions and Neon Postgres
Set `NEON_DATABASE_URL` in Streamlit secrets (or environment variable fallback) to enable CRUD action tracking.

## PoC limitations
- Uses synthetic data and lightweight Natural Earth polygons.
- Indicators are illustrative and not calibrated for operations.

## Plugging in real data later
- Replace `data/demo_signals.csv` with trusted feeds.
- Keep ISO3 alignment for map joins.
- Extend drivers and scenario templates with domain-specific coefficients.
"""
)
