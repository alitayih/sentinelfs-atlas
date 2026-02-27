# pages/1_Map_Home.py
import pandas as pd
import streamlit as st
from streamlit_plotly_events import plotly_events
import plotly.express as px

from sentinelfs.config import APP_TITLE, COMMODITIES, WINDOW_OPTIONS
from sentinelfs.data_store import aggregate_country_risk, ensure_session_defaults, load_demo_signals, load_geojson
from sentinelfs.map_engine import build_choropleth
from sentinelfs.risk_engine import compute_risk_score

st.set_page_config(page_title=f"{APP_TITLE} | Map Home", page_icon="🗺️", layout="wide")
st.title("Map Home")

ensure_session_defaults()

window_days = st.radio("Date window", WINDOW_OPTIONS, horizontal=True, index=0)
commodity = st.selectbox("Commodity", ["All", *COMMODITIES], index=0)
advanced_mode = st.toggle("Advanced mode", value=False)

# ✅ مجمّع على مستوى الدولة
country_risk = aggregate_country_risk(window_days, commodity)

left_col, right_col = st.columns([2.3, 1.2])

with left_col:
    geo = load_geojson()
    fig = build_choropleth(country_risk, geojson=geo, window_days=window_days, commodity=commodity)

    selected = plotly_events(fig, click_event=True, hover_event=False, key="map_click")

    with st.expander("Debug click payload", expanded=False):
        st.write(selected if selected else "No click captured yet.")

    if selected:
        p = selected[0]

        iso3 = p.get("location")
        if not iso3 and "pointNumber" in p:
            pn = p["pointNumber"]
            try:
                iso3 = fig.data[0].locations[pn]
            except Exception:
                try:
                    iso3 = fig.data[0].customdata[pn][0]
                except Exception:
                    iso3 = None

        if iso3:
            row = country_risk[country_risk["iso3"] == iso3].head(1)
            if not row.empty:
                st.session_state["selected_iso3"] = iso3
                st.session_state["selected_country_name"] = row.iloc[0]["country_name"]

                try:
                    st.switch_page("pages/2_Country_Focus.py")
                except Exception:
                    st.toast(f"Selected {iso3}. Open Country Focus from sidebar.", icon="📍")

with right_col:
    st.subheader("Quick KPIs")
    high_pct = (country_risk["risk_score"].gt(66).mean() * 100) if len(country_risk) else 0.0
    avg_score = country_risk["risk_score"].mean() if len(country_risk) else 0.0
    st.metric("High-risk countries", f"{high_pct:.1f}%")
    st.metric("Average risk", f"{avg_score:.1f}")

    st.subheader("Top risk (mean)")
    # risk_level قد لا يكون موجود (بنطلعه من risk_score)
    tmp = country_risk.copy()
    if "risk_level" not in tmp.columns:
        tmp["risk_level"] = tmp["risk_score"].apply(lambda s: "Low" if s <= 33 else ("Medium" if s <= 66 else "High"))

    st.dataframe(
        tmp.sort_values("risk_score", ascending=False).head(15)[["country_name", "iso3", "risk_score", "risk_level"]],
        hide_index=True,
        use_container_width=True,
    )

if advanced_mode:
    st.divider()
    st.subheader("Advanced analytics")

    raw = compute_risk_score(load_demo_signals())

    max_date = raw["date"].max()
    last14 = raw[raw["date"] >= max_date - pd.Timedelta(days=13)]
    prev14 = raw[(raw["date"] < max_date - pd.Timedelta(days=13)) & (raw["date"] >= max_date - pd.Timedelta(days=27))]

    if commodity != "All":
        last14 = last14[last14["commodity"] == commodity]
        prev14 = prev14[prev14["commodity"] == commodity]

    last_agg = last14.groupby(["iso3", "country_name"], as_index=False)["risk_score"].mean()
    prev_agg = (
        prev14.groupby(["iso3", "country_name"], as_index=False)["risk_score"]
        .mean()
        .rename(columns={"risk_score": "prev_risk_score"})
    )

    deltas = last_agg.merge(prev_agg, on=["iso3", "country_name"], how="left")
    deltas["delta_14d"] = deltas["risk_score"] - deltas["prev_risk_score"].fillna(deltas["risk_score"])

    r1, r2 = st.columns(2)
    with r1:
        st.write("Top Risers")
        st.dataframe(deltas.sort_values("delta_14d", ascending=False).head(10), hide_index=True, use_container_width=True)
    with r2:
        st.write("Top Fallers")
        st.dataframe(deltas.sort_values("delta_14d", ascending=True).head(10), hide_index=True, use_container_width=True)

    hist = px.histogram(country_risk, x="risk_score", nbins=20, title="Risk Score Distribution")
    st.plotly_chart(hist, use_container_width=True)
