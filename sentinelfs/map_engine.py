# sentinelfs/map_engine.py
from __future__ import annotations

import pandas as pd
import plotly.express as px


def build_choropleth(
    country_risk_df: pd.DataFrame,
    geojson: dict | None = None,   # ✅ صار optional
    window_days: int = 30,
    commodity: str = "All",
):
    plot_df = country_risk_df.copy()
    plot_df["window"] = f"Last {window_days} days"
    plot_df["commodity_view"] = commodity

    if "risk_level" not in plot_df.columns:
        plot_df["risk_level"] = plot_df["risk_score"].apply(
            lambda s: "Low" if s <= 33 else ("Medium" if s <= 66 else "High")
        )

    hover_data = {
        "iso3": True,
        "risk_score": ":.1f",
        "risk_level": True,
        "window": True,
        "commodity_view": True,
    }

    if geojson is None:
        fig = px.choropleth(
            plot_df,
            locations="iso3",
            locationmode="ISO-3",
            color="risk_score",
            hover_name="country_name",
            hover_data=hover_data,
            custom_data=["iso3", "country_name"],
            range_color=(0, 100),
            projection="natural earth",
            color_continuous_scale=[
                "#1a1a1a", "#2a2a2a", "#3a3a3a", "#4a4a4a", "#6a6a6a", "#9a9a9a", "#d0d0d0"
            ],
        )
        fig.update_geos(showframe=False, bgcolor="rgba(0,0,0,0)", fitbounds="locations")

    else:
        fig = px.choropleth(
            plot_df,
            geojson=geojson,
            featureidkey="properties.ISO_A3",
            locations="iso3",
            color="risk_score",
            hover_name="country_name",
            hover_data=hover_data,
            custom_data=["iso3", "country_name"],
            range_color=(0, 100),
            projection="natural earth",
            color_continuous_scale=[
                "#1a1a1a", "#2a2a2a", "#3a3a3a", "#4a4a4a", "#6a6a6a", "#9a9a9a", "#d0d0d0"
            ],
        )
        fig.update_geos(showframe=False, bgcolor="rgba(0,0,0,0)", fitbounds="locations")

    fig.update_traces(marker_line_width=0.7, marker_line_color="rgba(255,255,255,0.45)")
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        clickmode="event+select",
        dragmode="select",
        uirevision="map",
    )
    return fig
