import streamlit as st
import pandas as pd

from sentinelfs.config import APP_TITLE, COMMODITIES
from sentinelfs.data_store import load_demo_signals
from sentinelfs.risk_engine import compute_risk_score
from sentinelfs.scenarios import TEMPLATE_DELTAS, apply_scenario

st.set_page_config(page_title=f"{APP_TITLE} | Scenarios", page_icon="🧪", layout="wide")
st.title("Scenarios")

base = compute_risk_score(load_demo_signals())
countries = base[["iso3", "country_name"]].drop_duplicates().sort_values("country_name")
iso_opts = countries["iso3"].tolist()

col1, col2, col3, col4 = st.columns(4)
with col1:
    template = st.selectbox("Template", list(TEMPLATE_DELTAS.keys()))
with col2:
    target_iso3 = st.selectbox("Target country", iso_opts)
with col3:
    commodity = st.selectbox("Commodity", ["All", *COMMODITIES])
with col4:
    severity = st.slider("Severity", 0.0, 1.0, 0.5, 0.05)
duration = st.radio("Duration (days)", [7, 14, 30], horizontal=True)

scenario_df = apply_scenario(base, target_iso3, commodity, template, severity, duration)
scenario_df = compute_risk_score(scenario_df)

baseline = base.groupby(["iso3", "country_name"], as_index=False)["risk_score"].mean().rename(columns={"risk_score": "baseline"})
scenario = scenario_df.groupby(["iso3", "country_name"], as_index=False)["risk_score"].mean().rename(columns={"risk_score": "scenario"})
comparison = baseline.merge(scenario, on=["iso3", "country_name"])
comparison["delta"] = comparison["scenario"] - comparison["baseline"]

sel_name = countries[countries["iso3"] == target_iso3].iloc[0]["country_name"]
selected_row = comparison[comparison["iso3"] == target_iso3].iloc[0]
left, right = st.columns(2)
with left:
    st.subheader("Baseline vs Scenario")
    st.metric("Baseline risk", f"{selected_row['baseline']:.1f}")
    st.metric("Scenario risk", f"{selected_row['scenario']:.1f}", delta=f"{selected_row['delta']:.1f}")
    st.caption(f"Target: {sel_name} ({target_iso3})")
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
st.dataframe(pd.DataFrame(st.session_state["saved_scenarios"]), hide_index=True, use_container_width=True)
