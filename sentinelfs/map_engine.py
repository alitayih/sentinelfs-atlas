# sentinelfs/map_engine.py
from __future__ import annotations

import pandas as pd
import plotly.express as px


def _risk_level_from_score(score: float) -> str:
    if score <= 33:
        return "Low"
    if score <= 66:
        return "Medium"
    return "High"


def build_choropleth(
    country_risk_df: pd.DataFrame,
    window_days: int,
    commodity: str,
):
    """
    Fast choropleth (NO GeoJSON injection).
    Uses ISO-3 locations only -> much smaller payload, faster reruns.
    """
    plot_df = country_risk_df.copy()

    # Ensure risk_level exists for hover
    if "risk_level" not in plot_df.columns:
        plot_df["risk_level"] = plot_df["risk_score"].apply(_risk_level_from_score)

    plot_df["window"] = f"Last {window_days} days"
    plot_df["commodity_view"] = commodity

    fig = px.choropleth(
        plot_df,
        locations="iso3",
        locationmode="ISO-3",
        color="risk_score",
        hover_name="country_name",
        hover_data={
            "iso3": True,
            "risk_score": ":.1f",
            "risk_level": True,
            "window": True,
            "commodity_view": True,
        },
        custom_data=["iso3", "country_name"],
        range_color=(0, 100),
        projection="natural earth",
        color_continuous_scale=[
            "#1a1a1a",
            "#2a2a2a",
            "#3a3a3a",
            "#4a4a4a",
            "#6a6a6a",
            "#9a9a9a",
            "#d0d0d0",
        ],
    )

    # Borders
    fig.update_traces(marker_line_width=0.7, marker_line_color="rgba(255,255,255,0.45)")

    # Clean geo styling
    fig.update_geos(
        showcountries=True,
        showcoastlines=False,
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
        fitbounds="locations",
    )

    # Click/select behavior
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        clickmode="event+select",
        dragmode="select",
        uirevision="map",
        coloraxis_colorbar=dict(
            title=dict(text="Risk", font=dict(color="white")),
            tickfont=dict(color="white"),
        ),
    )

    return fig
