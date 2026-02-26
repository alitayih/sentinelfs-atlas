import pandas as pd
import streamlit as st

from sentinelfs.actions_db import (
    delete_action,
    ensure_actions_table,
    get_engine,
    insert_action,
    list_actions,
    update_action_status,
)
from sentinelfs.config import APP_TITLE, COMMODITIES
from sentinelfs.data_store import load_demo_signals
from sentinelfs.risk_engine import compute_risk_score
from sentinelfs.ui import sigmoid

st.set_page_config(page_title=f"{APP_TITLE} | Action Tracking", page_icon="✅", layout="wide")
st.title("Action Tracking")

engine = get_engine()
if engine is None:
    st.error("NEON_DATABASE_URL not found in secrets or environment. Configure Neon to enable Action Tracking.")
    st.stop()

ensure_actions_table(engine)
raw = compute_risk_score(load_demo_signals())

with st.expander("Add action", expanded=True):
    c1, c2, c3 = st.columns(3)
    title = c1.text_input("Title")
    owner = c2.text_input("Owner")
    due_date = c3.date_input("Due date", value=None)

    c4, c5, c6 = st.columns(3)
    status = c4.selectbox("Status", ["Open", "In Progress", "Blocked", "Done"])
    commodity = c5.selectbox("Commodity", ["All", *COMMODITIES])
    country_iso3 = c6.text_input("Country ISO3", max_chars=3).upper()

    expected_risk_impact = st.text_input("Expected risk impact")
    notes = st.text_area("Notes")

    if st.button("Create action") and title:
        payload = {
            "title": title,
            "owner": owner or None,
            "due_date": due_date,
            "status": status,
            "commodity": commodity,
            "country_iso3": country_iso3 or None,
            "expected_risk_impact": expected_risk_impact or None,
            "notes": notes or None,
        }
        insert_action(engine, payload)
        st.success("Action created.")

actions = list_actions(engine)
if actions.empty:
    st.info("No actions yet.")
else:
    actions["due_date"] = pd.to_datetime(actions["due_date"], errors="coerce")
    today = pd.Timestamp.today().normalize()
    open_actions = actions[actions["status"].isin(["Open", "In Progress", "Blocked"])]
    overdue = open_actions[open_actions["due_date"].notna() & (open_actions["due_date"] < today)]

    avg_risk = raw["risk_score"].mean()
    escalation_probability = sigmoid((avg_risk / 100) * 2 + (len(open_actions) / 20) - 1)

    m1, m2, m3 = st.columns(3)
    m1.metric("Open actions", len(open_actions))
    m2.metric("Overdue", len(overdue))
    m3.metric("Escalation probability", f"{escalation_probability:.2%}")

    change_30d = (
        raw.groupby("date", as_index=False)[["conflict_intensity", "freight_volatility"]]
        .mean()
        .sort_values("date")
    )
    change_30d["conflict_trend_30d"] = change_30d["conflict_intensity"] - change_30d["conflict_intensity"].shift(30)
    change_30d["freight_trend_30d"] = change_30d["freight_volatility"] - change_30d["freight_volatility"].shift(30)
    latest = change_30d.iloc[-1]
    st.caption(
        f"Conflict trend (30d): {latest['conflict_trend_30d']:.3f} | Freight indicator (30d): {latest['freight_trend_30d']:.3f}"
    )

    filter_status = st.multiselect("Filter status", sorted(actions["status"].dropna().unique()), default=[])
    filter_iso3 = st.text_input("Filter country ISO3").upper()
    filtered = actions.copy()
    if filter_status:
        filtered = filtered[filtered["status"].isin(filter_status)]
    if filter_iso3:
        filtered = filtered[filtered["country_iso3"] == filter_iso3]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.subheader("Update or Delete")
    ids = filtered["id"].tolist()
    if ids:
        selected_id = st.selectbox("Action ID", ids)
        new_status = st.selectbox("New status", ["Open", "In Progress", "Blocked", "Done"])
        c_upd, c_del = st.columns(2)
        if c_upd.button("Update status"):
            update_action_status(engine, int(selected_id), new_status)
            st.success("Status updated. Refresh page to see latest table ordering.")
        if c_del.button("Delete action"):
            delete_action(engine, int(selected_id))
            st.warning("Action deleted. Refresh page to see latest table.")
