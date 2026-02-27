from __future__ import annotations

import pandas as pd
import streamlit as st

from sentinelfs.config import APP_TITLE, COMMODITIES, WINDOW_OPTIONS
from sentinelfs.data_store import load_demo_signals_cached
from sentinelfs.risk_engine import compute_risk_score
from sentinelfs.scenarios import TEMPLATE_DELTAS, apply_scenario
from sentinelfs.ui import inject_css, ensure_ui_state, sidebar_filters

st.set_page_config(page_title=f"{APP_TITLE} | Scenarios", page_icon="🧪", layout="wide")
inject_css()
ensure_ui_state()

st.title("Scenarios")
st.caption("Mock scenario simulation • fast cached baseline")

window_days, global_commodity, advanced_mode, _auto_open = sidebar_filters(WINDOW_OPTIONS, COMMODITIES)

@st.cache_data(ttl=3600, show_spinner=False)
def baseline_scored() -> pd.DataFrame:
    return compute_risk_score(load_demo_signals_cached())

@st.cache_data(ttl=3600, show_spinner=False)
def baseline_filtered(base: pd.DataFrame, window_days: int, commodity: str) -> pd.DataFrame:
    if base.empty:
        return base
    max_date = base["date"].max()
    start_date = max_date - pd.Timedelta(days=window_days - 1)
    out = base[base["date"] >= start_date]
    if commodity != "All":
        out = out[out["commodity"] == commodity]
    return out

base_all = baseline_scored()
base = baseline_filtered(base_all, window_days, "All")  # keep all commodities for scenarios; apply later

countries = base[["iso3", "country_name"]].drop_duplicates().sort_values("country_name")
iso_opts = countries["iso3"].tolist()

col1, col2, col3, col4 = st.columns(4)
with col1:
    template = st.selectbox("Template", list(TEMPLATE_DELTAS.keys()))
with col2:
    default_iso = st.session_state.get("selected_iso3")
    if default_iso not in iso_opts:
        default_iso = iso_opts[0]
    target_iso3 = st.selectbox("Target country", iso_opts, index=iso_opts.index(default_iso))
with col3:
    commodity = st.selectbox("Commodity", ["All", *COMMODITIES], index=(["All", *COMMODITIES].index(global_commodity) if global_commodity in ["All", *COMMODITIES] else 0))
with col4:
    severity = st.slider("Severity", 0.0, 1.0, 0.5, 0.05)

duration = st.radio("Duration (days)", [7, 14, 30], horizontal=True)

scenario_df = apply_scenario(base, target_iso3, commodity, template, severity, duration)
scenario_df = compute_risk_score(scenario_df)

baseline = base.groupby(["iso3", "country_name"], as_index=False)["risk_score"].mean().rename(columns={"risk_score": "baseline"})
scenario = scenario_df.groupby(["iso3", "country_name"], as_index=False)["risk_score"].mean().rename(columns={"risk_score": "scenario"})
comparison = baseline.merge(scenario, on=["iso3", "country_name"], how="left")
comparison["delta"] = comparison["scenario"] - comparison["baseline"]

sel_name = countries[countries["iso3"] == target_iso3].iloc[0]["country_name"]
selected_row = comparison[comparison["iso3"] == target_iso3].iloc[0]

left, right = st.columns(2)
with left:
    st.subheader("Baseline vs Scenario")
    st.metric("Baseline risk", f"{selected_row['baseline']:.1f}")
    st.metric("Scenario risk", f"{selected_row['scenario']:.1f}", delta=f"{selected_row['delta']:.1f}")
    st.caption(f"Target: {sel_name} ({target_iso3}) • Window: {window_days}d")
with right:
    st.subheader("Top impacted countries (delta)")
    st.dataframe(
        comparison.sort_values("delta", ascending=False).head(20)[["country_name", "iso3", "baseline", "scenario", "delta"]],
        hide_index=True,
        use_container_width=True,
    )

if "saved_scenarios" not in st.session_state:
    st.session_state["saved_scenarios"] = []

if st.button("Save scenario"):
    st.session_state["saved_scenarios"].append(
        {
            "template": template,
            "target_iso3": target_iso3,
            "commodity": commodity,
            "severity": severity,
            "duration": duration,
            "target_delta": float(selected_row["delta"]),
        }
    )

st.subheader("Saved scenarios")
if st.session_state["saved_scenarios"]:
    st.dataframe(pd.DataFrame(st.session_state["saved_scenarios"]), hide_index=True, use_container_width=True)
else:
    st.caption("No saved scenarios yet.")
