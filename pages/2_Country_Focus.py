import streamlit as st
import plotly.express as px
import pandas as pd

from sentinelfs.config import APP_TITLE
from sentinelfs.data_store import ensure_session_defaults, load_demo_signals
from sentinelfs.risk_engine import compute_risk_score

st.set_page_config(page_title=f"{APP_TITLE} | Country Focus", page_icon="📍", layout="wide")
st.title("Country Focus")
st.caption("Badge: demo/synthetic")

selected_iso3, _ = ensure_session_defaults()
raw = compute_risk_score(load_demo_signals())

countries = raw[["iso3", "country_name"]].drop_duplicates().sort_values("country_name")
iso3_options = countries["iso3"].tolist()
if selected_iso3 not in iso3_options:
    selected_iso3 = iso3_options[0]

chosen_iso3 = st.selectbox("Country (ISO3)", iso3_options, index=iso3_options.index(selected_iso3))
country_name = countries[countries["iso3"] == chosen_iso3].iloc[0]["country_name"]
st.session_state["selected_iso3"] = chosen_iso3
st.session_state["selected_country_name"] = country_name

country_df = raw[raw["iso3"] == chosen_iso3].sort_values("date")

ts = country_df.groupby("date", as_index=False)["risk_score"].mean()
fig_risk = px.line(ts, x="date", y="risk_score", title=f"{country_name} Risk Score (180d)")
st.plotly_chart(fig_risk, use_container_width=True)

driver_cols = [
    "conflict_intensity",
    "freight_volatility",
    "export_restriction_sentiment",
    "price_shock",
    "weather_risk",
]
driver_ts = country_df.groupby("date", as_index=False)[driver_cols].mean()
driver_long = driver_ts.melt(id_vars="date", var_name="driver", value_name="value")
fig_driver = px.line(driver_long, x="date", y="value", color="driver", title="Driver Trends")
st.plotly_chart(fig_driver, use_container_width=True)

risk_daily = ts.copy()
risk_daily["avg_7d"] = risk_daily["risk_score"].rolling(7).mean()
risk_daily["prev_7d"] = risk_daily["avg_7d"].shift(7)
risk_daily["delta_7d"] = risk_daily["avg_7d"] - risk_daily["prev_7d"]
spikes = risk_daily[risk_daily["delta_7d"] > 10][["date", "avg_7d", "prev_7d", "delta_7d"]]

st.subheader("Spike Events")
if spikes.empty:
    st.success("No spike events detected using 7-day average threshold > 10.")
else:
    st.dataframe(spikes.sort_values("date", ascending=False), hide_index=True, use_container_width=True)
