import json
from typing import Tuple

import pandas as pd
import streamlit as st

from sentinelfs.config import DEMO_SIGNALS_PATH, WORLD_GEOJSON_PATH
from sentinelfs.risk_engine import compute_risk_score


@st.cache_data(show_spinner=False)
def load_demo_signals() -> pd.DataFrame:
    df = pd.read_csv(DEMO_SIGNALS_PATH, parse_dates=["date"])
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_demo_signals_cached():
    # استدعاء دالتك الأصلية
    return load_demo_signals()


@st.cache_data(show_spinner=False)
def load_geojson() -> dict:
    with open(WORLD_GEOJSON_PATH, "r", encoding="utf-8") as f:
        geo = json.load(f)

    for feature in geo.get("features", []):
        props = feature.setdefault("properties", {})
        iso3 = props.get("ISO_A3") or props.get("ADM0_A3") or props.get("SOV_A3")
        if not iso3:
            iso3 = props.get("iso_a3") or props.get("id")
        props["ISO_A3"] = iso3
    return geo


@st.cache_data(show_spinner=False)
def filtered_signals(window_days: int, commodity: str) -> pd.DataFrame:
    df = load_demo_signals().copy()
    max_date = df["date"].max()
    start_date = max_date - pd.Timedelta(days=window_days - 1)
    df = df[df["date"] >= start_date]
    if commodity != "All":
        df = df[df["commodity"] == commodity]
    return df


@st.cache_data(show_spinner=False)
def aggregate_country_risk(window_days: int, commodity: str) -> pd.DataFrame:
    df = compute_risk_score(filtered_signals(window_days, commodity))
    numeric_cols = [
        "conflict_intensity",
        "freight_volatility",
        "export_restriction_sentiment",
        "price_shock",
        "weather_risk",
        "risk_score",
    ]
    agg = (
        df.groupby(["iso3", "country_name"], as_index=False)[numeric_cols]
        .mean(numeric_only=True)
        .sort_values("risk_score", ascending=False)
    )
    return agg


def ensure_session_defaults() -> Tuple[str, str]:
    selected_iso3 = st.session_state.get("selected_iso3", "USA")
    selected_country_name = st.session_state.get("selected_country_name", "United States of America")
    st.session_state["selected_iso3"] = selected_iso3
    st.session_state["selected_country_name"] = selected_country_name
    return selected_iso3, selected_country_name
