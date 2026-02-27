# sentinelfs/ui.py
from __future__ import annotations
import streamlit as st


def inject_css():
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
          section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }
          header[data-testid="stHeader"] { height: 0.5rem; }

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
        "auto_open_on_click": True,   # ✅ بدك الاثنين
        "selected_iso3": None,
        "selected_country_name": None,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def sidebar_filters(WINDOW_OPTIONS, COMMODITIES):
    """
    ✅ يرجّع 4 قيم:
    window_days, commodity, advanced_mode, auto_open
    """
    with st.sidebar:
        st.markdown("### Controls")

        wd = st.session_state.get("window_days", WINDOW_OPTIONS[0])
        wd_idx = WINDOW_OPTIONS.index(wd) if wd in WINDOW_OPTIONS else 0
        window_days = st.radio("Date window", WINDOW_OPTIONS, horizontal=True, index=wd_idx, key="window_days")

        commodity_list = ["All", *COMMODITIES]
        com = st.session_state.get("commodity", "All")
        com_idx = commodity_list.index(com) if com in commodity_list else 0
        commodity = st.selectbox("Commodity", commodity_list, index=com_idx, key="commodity")

        advanced_mode = st.toggle("Advanced mode", value=st.session_state.get("advanced_mode", False), key="advanced_mode")

        auto_open = st.toggle(
            "Auto-open Country Focus on click",
            value=st.session_state.get("auto_open_on_click", True),
            key="auto_open_on_click",
        )

        st.markdown("---")
        st.caption("SentinelFS Atlas • Mock data mode")

    return window_days, commodity, advanced_mode, auto_open


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



def sigmoid(x: float) -> float:
    """Small helper for UI metrics."""
    import math
    return 1.0 / (1.0 + math.exp(-x))

import math

def sigmoid(x: float) -> float:
    # stable sigmoid (prevents overflow)
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    else:
        z = math.exp(x)
        return z / (1 + z)
