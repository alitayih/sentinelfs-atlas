# pages/1_Map_Home.py
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_plotly_events import plotly_events

from sentinelfs.config import APP_TITLE, COMMODITIES, WINDOW_OPTIONS
from sentinelfs.data_store import aggregate_country_risk, load_demo_signals
from sentinelfs.map_engine import build_choropleth
from sentinelfs.risk_engine import compute_risk_score
from sentinelfs.ui import inject_css, ensure_ui_state, sidebar_filters, kpi_card


st.set_page_config(page_title=f"{APP_TITLE} | Map Home", page_icon="🗺️", layout="wide")
inject_css()
ensure_ui_state()

st.title("SentinelFS Atlas")
st.caption("Operational early-warning dashboard (Mock mode)")

# ✅ Global filters (sidebar)
window_days, commodity, advanced_mode = sidebar_filters(WINDOW_OPTIONS, COMMODITIES)

# ✅ Aggregated risk per country (fast)
country_risk = aggregate_country_risk(window_days, commodity)
if "risk_level" not in country_risk.columns:
    country_risk = compute_risk_score(country_risk)

# ---------- KPI Row ----------
# Compute risers/fallers from mock raw ONLY once (cached by Streamlit via load_demo_signals if you cache it there)
raw = None
if advanced_mode:
    raw = compute_risk_score(load_demo_signals())

# Minimal KPI derivations (fast)
avg_score = float(country_risk["risk_score"].mean()) if len(country_risk) else 0.0
high_pct = float((country_risk["risk_level"].eq("High").mean() * 100)) if len(country_risk) else 0.0

# Risers/fallers (only if raw exists, else show placeholders)
riser_txt, faller_txt = "—", "—"
riser_sub, faller_sub = "Enable Advanced mode", "Enable Advanced mode"

if raw is not None and len(raw):
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

    top_riser = deltas.sort_values("delta_14d", ascending=False).head(1)
    top_faller = deltas.sort_values("delta_14d", ascending=True).head(1)

    if len(top_riser):
        riser_txt = top_riser.iloc[0]["country_name"]
        riser_sub = f"+{top_riser.iloc[0]['delta_14d']:.1f} (14d)"
    if len(top_faller):
        faller_txt = top_faller.iloc[0]["country_name"]
        faller_sub = f"{top_faller.iloc[0]['delta_14d']:.1f} (14d)"

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("High-risk countries", f"{high_pct:.1f}%", "Risk level = High")
with k2:
    kpi_card("Average risk", f"{avg_score:.1f}", f"Window: {window_days}d")
with k3:
    kpi_card("Biggest riser", riser_txt, riser_sub)
with k4:
    kpi_card("Biggest faller", faller_txt, faller_sub)

st.markdown("---")

# ---------- Main Layout ----------
left_col, right_col = st.columns([2.3, 1.2])

with left_col:
    fig = build_choropleth(
        country_risk_df=country_risk,
        geojson=None,  # ✅ fastest
        window_days=window_days,
        commodity=commodity,
    )

    selected = plotly_events(
        fig,
        click_event=True,
        select_event=True,
        hover_event=False,
        key="map_events",
    )

    # Friendly selection strip
    sel = selected[0].get("location") if selected else None
    if sel:
        st.session_state["selected_iso3"] = sel
        name = country_risk.loc[country_risk["iso3"] == sel, "country_name"].head(1)
        st.session_state["selected_country_name"] = name.iloc[0] if len(name) else sel
        st.info(f"Selected: **{st.session_state['selected_country_name']}**  •  Click again or use the button to open details.")

        cta1, cta2 = st.columns([1, 3])
        with cta1:
            if st.button("Open details", use_container_width=True):
                st.switch_page("pages/2_Country_Focus.py")
                st.stop()

    # Tabs under map
    t1, t2, t3 = st.tabs(["Drivers", "Risers & Fallers", "Alerts (Mock)"])

    with t1:
        # Simple global drivers from aggregated table
        driver_cols = [c for c in ["conflict_intensity", "freight_volatility", "export_restriction_sentiment", "price_shock", "weather_risk"] if c in country_risk.columns]
        if not driver_cols:
            st.caption("No driver columns available in this view.")
        else:
            drivers = country_risk[driver_cols].mean().reset_index()
            drivers.columns = ["driver", "mean_value"]
            drivers = drivers.sort_values("mean_value", ascending=False)
            figd = px.bar(drivers, x="driver", y="mean_value", title="Global driver intensity (mean)")
            st.plotly_chart(figd, use_container_width=True)

    with t2:
        if raw is None:
            st.caption("Enable **Advanced mode** to compute 14-day deltas (mock).")
        else:
            # reuse deltas from above if exists, else compute quickly
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

            a, b = st.columns(2)
            with a:
                st.write("Top Risers")
                st.dataframe(
                    deltas.sort_values("delta_14d", ascending=False).head(10)[["country_name", "iso3", "risk_score", "delta_14d"]],
                    hide_index=True,
                    use_container_width=True,
                )
            with b:
                st.write("Top Fallers")
                st.dataframe(
                    deltas.sort_values("delta_14d", ascending=True).head(10)[["country_name", "iso3", "risk_score", "delta_14d"]],
                    hide_index=True,
                    use_container_width=True,
                )

    with t3:
        # Mock alert feed (no real data yet)
        alerts = [
            {"time": "2h ago", "severity": "High", "title": "Export restriction chatter increased", "area": "Multiple"},
            {"time": "6h ago", "severity": "Medium", "title": "Freight volatility elevated", "area": "Red Sea route"},
            {"time": "1d ago", "severity": "Medium", "title": "Weather anomaly detected", "area": "North Africa"},
            {"time": "2d ago", "severity": "Low", "title": "Commodity price noise", "area": "Global"},
        ]
        for a in alerts:
            st.markdown(
                f"""
                <div class="sfs-card" style="margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;gap:10px;">
                    <div style="font-weight:700;">{a['title']}</div>
                    <div style="opacity:0.75;">{a['time']}</div>
                  </div>
                  <div style="opacity:0.75;margin-top:6px;">
                    Severity: <b>{a['severity']}</b> • Area: {a['area']}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with right_col:
    st.subheader("Top risk (mean)")
    st.dataframe(
        country_risk.sort_values("risk_score", ascending=False).head(15)[
            ["country_name", "iso3", "risk_score", "risk_level"]
        ],
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Notes")
    st.caption(
        "This is a mock-data build focused on UI/UX, flows, and operational layer. "
        "Data connectors will be plugged in later without changing the app structure."
    )
