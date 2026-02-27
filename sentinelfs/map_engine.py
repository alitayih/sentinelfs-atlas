import pandas as pd
import plotly.express as px


def build_choropleth(country_risk_df: pd.DataFrame, geojson: dict, window_days: int, commodity: str):
    plot_df = country_risk_df.copy()
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
        color_continuous_scale=["#0b0b0b", "#1a1a1a", "#2a2a2a", "#3a3a3a", "#4a4a4a", "#5a5a5a", "#6a6a6a"],
        range_color=(0, 100),
        projection="natural earth",
    )

    fig.update_traces(marker_line_width=0.6, marker_line_color="rgba(255,255,255,0.35)")
    fig.update_geos(showcoastlines=False, showframe=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title=dict(text="Risk", font=dict(color="white")),
            tickfont=dict(color="white"),
        ),
    )
    return fig
