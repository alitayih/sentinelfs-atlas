from __future__ import annotations

import streamlit as st

from sentinelfs.config import APP_TITLE, COMMODITIES, WINDOW_OPTIONS
from sentinelfs.ui import inject_css, ensure_ui_state, sidebar_filters

st.set_page_config(page_title=f"{APP_TITLE} | Help", page_icon="📘", layout="wide")
inject_css()
ensure_ui_state()

st.title("Help & User Manual")

# Keep sidebar consistent (controls visible, but do not affect this page content)
sidebar_filters(WINDOW_OPTIONS, COMMODITIES)

st.markdown(
    """
### What is SentinelFS Atlas?
A lightweight mock-data early-warning dashboard for food-security and geopolitical risk monitoring.

### How to use the Map Home
- Use **Date window** and **Commodity** in the sidebar.
- Click a country to open **Country Focus** (or disable auto-open to use the button).

### Country Focus
- Explore the risk trend and drivers for a selected country.
- The explainability panel highlights the strongest drivers.

### Scenarios
- Choose a scenario template and simulate shocks.
- Save scenarios for quick comparison.

### Action Tracking
- Track operational actions, owners, due dates, and status.
- Uses Neon/Postgres when configured via `NEON_DATABASE_URL`.

> This is a mock-data build. Real data connectors can be added later without changing the UI structure.
"""
)
