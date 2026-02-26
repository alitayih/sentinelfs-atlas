import streamlit as st

from sentinelfs.config import APP_TITLE

st.set_page_config(page_title=APP_TITLE, page_icon="🌍", layout="wide")

st.title(APP_TITLE)
st.markdown(
    """
Welcome to **SentinelFS Atlas**, a decision-support prototype for country-level food system risk.
Use the left sidebar to navigate pages:
- Map Home
- Country Focus
- Scenarios
- Action Tracking
- Help User Manual
"""
)

st.info("Streamlit multipage navigation is enabled through the pages/ directory.")
st.page_link("pages/1_Map_Home.py", label="Open Map Home", icon="🗺️")
