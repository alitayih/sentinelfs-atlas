from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from sentinelfs.config import APP_TITLE, COMMODITIES, WINDOW_OPTIONS
from sentinelfs.data_store import load_demo_signals_cached
from sentinelfs.risk_engine import compute_risk_score
from sentinelfs.ui import inject_css, ensure_ui_state, sidebar_filters

st.set_page_config(page_title=f"{APP_TITLE} | Country Focus", page_icon="📍", layout="wide")
inject_css()
ensure_ui_state()

st.title("Country Focus")
st.caption("Mock-data view • fast cached scoring")

# Global filters (shared with Map Home)
window_days, commodity, advanced_mode, _auto_open = sidebar_filters(WINDOW_OPTIONS, COMMODITIES)

@st.cache_data(ttl=3600, show_spinner=False)
def load_scored_signals() -> pd.DataFrame:
    df = load_demo_signals_cached()
    return compute_risk_score(df)

@st.cache_data(ttl=3600, show_spinner=False)
def filtered_scored(scored: pd.DataFrame, window_days: int, commodity: str) -> pd.DataFrame:
    if scored.empty:
        return scored
    max_date = scored["date"].max()
    start_date = max_date - pd.Timedelta(days=window_days - 1)
    out = scored[scored["date"] >= start_date]
    if commodity != "All":
        out = out[out["commodity"] == commodity]
    return out

scored = load_scored_signals()
scored = filtered_scored(scored, window_days, commodity)

if scored.empty:
    st.info("No data for the current filters.")
    st.stop()

countries = scored[["iso3", "country_name"]].drop_duplicates().sort_values("country_name")
iso_opts = countries["iso3"].tolist()

# preselect from session_state if set
default_iso = st.session_state.get("selected_iso3")
if default_iso not in iso_opts:
    default_iso = iso_opts[0]

c1, c2 = st.columns([2, 1])
with c1:
    iso3 = st.selectbox("Country", iso_opts, index=iso_opts.index(default_iso))
with c2:
    st.metric("Window", f"{window_days} days")
    st.metric("Commodity", commodity)

st.session_state["selected_iso3"] = iso3
st.session_state["selected_country_name"] = countries[countries["iso3"] == iso3].iloc[0]["country_name"]

country_df = scored[scored["iso3"] == iso3].sort_values("date")

# --- Summary cards ---
avg_risk = float(country_df["risk_score"].mean()) if len(country_df) else 0.0
latest = country_df.iloc[-1] if len(country_df) else None

m1, m2, m3 = st.columns(3)
m1.metric("Average risk", f"{avg_risk:.1f}")
if latest is not None:
    m2.metric("Latest risk", f"{latest['risk_score']:.1f}", delta=None)
    m3.metric("Risk level", str(latest.get("risk_level", "")))
else:
    m2.metric("Latest risk", "—")
    m3.metric("Risk level", "—")

# --- Time series ---
ts = country_df.groupby("date", as_index=False)["risk_score"].mean()
fig_ts = px.line(ts, x="date", y="risk_score", title="Risk score over time")
st.plotly_chart(fig_ts, use_container_width=True)

# --- Drivers ---
driver_cols = [
    "conflict_intensity",
    "freight_volatility",
    "export_restriction_sentiment",
    "price_shock",
    "weather_risk",
]
available = [c for c in driver_cols if c in country_df.columns]
if available:
    drv = country_df.groupby("date", as_index=False)[available].mean()
    fig_drv = px.line(drv, x="date", y=available, title="Drivers over time")
    st.plotly_chart(fig_drv, use_container_width=True)

# --- Explanation panel (mock) ---
with st.expander("Why is risk high? (explainability)", expanded=True):
    if latest is None:
        st.caption("No latest row.")
    else:
        # simple ranking of drivers by latest value
        pairs = [(c, float(latest[c])) for c in available]
        pairs.sort(key=lambda x: x[1], reverse=True)
        top = pairs[:3]
        st.write("Top drivers (latest):")
        for k, v in top:
            st.write(f"- **{k}**: {v:.3f}")

        st.caption("Tip: When real data is connected, this panel will cite sources and show deltas.")

