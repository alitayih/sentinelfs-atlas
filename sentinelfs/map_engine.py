# sentinelfs/map_engine.py
import pandas as pd
import plotly.express as px


def build_choropleth(country_risk_df: pd.DataFrame, geojson: dict, window_days: int, commodity: str):
    plot_df = country_risk_df.copy()
    plot_df["window"] = f"Last {window_days} days"
    plot_df["commodity_view"] = commodity

    fig = px.choropleth(
        plot_df,
        geojson=geojson,
        featureidkey="properties.ISO_A3",
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
    )

    # خريطة أنظف + تثبيت الهايلايت + إظهار borders بشكل واضح
    fig.update_geos(
        fitbounds="locations",
        showcountries=True,
        showcoastlines=False,
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        clickmode="event+select",
        uirevision="map",
        coloraxis_colorbar=dict(
            title=dict(text="Risk", font=dict(color="white")),
            tickfont=dict(color="white"),
        ),
    )

    # هايلايت واضح للدولة المختارة
    fig.update_traces(
        marker_line_width=0.6,
        marker_line_color="rgba(255,255,255,0.35)",
        selected=dict(marker_line_width=2.2, marker_line_color="rgba(57,255,182,0.95)"),
        unselected=dict(marker_opacity=0.78),
    )

    return fig
