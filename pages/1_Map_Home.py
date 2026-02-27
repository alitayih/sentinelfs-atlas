import pandas as pd
import streamlit as st
from streamlit_plotly_events import plotly_events
import plotly.express as px

from sentinelfs.config import APP_TITLE, COMMODITIES, WINDOW_OPTIONS
from sentinelfs.data_store import aggregate_country_risk, ensure_session_defaults, load_demo_signals
from sentinelfs.map_engine import build_choropleth
from sentinelfs.risk_engine import compute_risk_score
from sentinelfs.ui import format_risk_metrics

st.set_page_config(page_title=f"{APP_TITLE} | Map Home", page_icon="🗺️", layout="wide")
st.title("Map Home")

window_days = st.radio("Date window", WINDOW_OPTIONS, horizontal=True, index=0)
commodity = st.selectbox("Commodity", ["All", *COMMODITIES], index=0)
advanced_mode = st.toggle("Advanced mode", value=False)

raw = compute_risk_score(load_demo_signals())
country_risk = aggregate_country_risk(window_days, commodity)
country_risk = compute_risk_score(country_risk)

left_col, right_col = st.columns([2.3, 1.2])

with left_col:
    fig = build_choropleth(country_risk, geojson=None, window_days=window_days, commodity=commodity)

    selected = plotly_events(fig, click_event=True, hover_event=False, key="map_click")

    # Debug (اختياري)
    with st.expander("Debug click payload", expanded=False):
        st.write(selected if selected else "No click captured yet.")

    if selected:
        p = selected[0]

        # 1) حاول مباشرة (أحياناً موجود)
        iso3 = p.get("location")

        # 2) لو مش موجودة، استخدم pointNumber (الأكثر شيوعاً)
        if not iso3 and "pointNumber" in p:
            pn = p["pointNumber"]
            try:
                # الأفضل: locations
                iso3 = fig.data[0].locations[pn]
            except Exception:
                # بديل: customdata
                try:
                    iso3 = fig.data[0].customdata[pn][0]
                except Exception:
                    iso3 = None

        if iso3:
            row = country_risk[country_risk["iso3"] == iso3].head(1)
            if not row.empty:
                st.session_state["selected_iso3"] = iso3
                st.session_state["selected_country_name"] = row.iloc[0]["country_name"]

                # ✅ نقل فوري للتفاصيل
                try:
                    st.switch_page("pages/2_Country_Focus.py")
                except Exception:
                    st.toast(f"Selected {iso3}. Use the button to open Country Focus.", icon="📍")

if advanced_mode:
    st.divider()
    st.subheader("Advanced analytics")

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
