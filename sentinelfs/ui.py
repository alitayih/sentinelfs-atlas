# sentinelfs/ui.py
from __future__ import annotations

import streamlit as st


def inject_css():
    st.markdown(
        """
        <style>
          /* Page padding */
          .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

          /* Sidebar spacing */
          section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }

          /* Reduce top whitespace */
          header[data-testid="stHeader"] { height: 0.5rem; }

          /* Cards look */
          .sfs-card {
            background: rgba(17, 24, 39, 0.85);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 14px 14px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
          }
          .sfs-kpi-title { font-size: 0.85rem; color: rgba(229,231,235,0.75); margin-bottom: 4px; }
          .sfs-kpi-value { font-size: 1.55rem; font-weight: 700; color: #E5E7EB; line-height: 1.2; }
          .sfs-kpi-sub { font-size: 0.82rem; color: rgba(229,231,235,0.65); margin-top: 6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_ui_state():
    defaults = {
        "window_days": 30,
        "commodity": "All",
        "advanced_mode": False,
        "selected_iso3": None,
        "selected_country_name": None,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def sidebar_filters(WINDOW_OPTIONS, COMMODITIES):
    """
    Global sidebar filters for all pages.
    Uses session_state so navigation keeps selections.
    """
    with st.sidebar:
        st.markdown("### Controls")
        window_days = st.radio(
            "Date window",
            WINDOW_OPTIONS,
            horizontal=True,
            index=0 if st.session_state["window_days"] == WINDOW_OPTIONS[0] else 1,
            key="window_days",
        )

        commodity = st.selectbox(
            "Commodity",
            ["All", *COMMODITIES],
            index=(["All", *COMMODITIES].index(st.session_state["commodity"])
                   if st.session_state["commodity"] in ["All", *COMMODITIES] else 0),
            key="commodity",
        )

        advanced_mode = st.toggle("Advanced mode", value=st.session_state["advanced_mode"], key="advanced_mode")

        st.markdown("---")
        st.caption("SentinelFS Atlas • Mock data mode")

    return window_days, commodity, advanced_mode


def kpi_card(title: str, value: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="sfs-card">
          <div class="sfs-kpi-title">{title}</div>
          <div class="sfs-kpi-value">{value}</div>
          <div class="sfs-kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
