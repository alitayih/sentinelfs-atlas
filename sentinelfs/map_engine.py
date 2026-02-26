import pandas as pd
import plotly.express as px


RISK_COLORS = {
    "Low": "#2ca02c",
    "Medium": "#f1c40f",
    "High": "#d62728",
}


def build_choropleth(country_risk_df: pd.DataFrame, geojson: dict | None, window_days: int, commodity: str):
    plot_df = country_risk_df.copy()
    plot_df["window_days"] = f"Last {window_days} days"
    plot_df["commodity_view"] = commodity

    fig = px.choropleth(
        plot_df,
        locations="iso3",
        locationmode="ISO-3",
        color="risk_level",
        color_discrete_map=RISK_COLORS,
        category_orders={"risk_level": ["Low", "Medium", "High"]},
        hover_name="country_name",
        hover_data={
            "country_name": False,
            "iso3": True,
            "risk_score": ':.1f',
            "risk_level": True,
            "window_days": True,
            "commodity_view": True,
        },
        scope="world",
        projection="natural earth",
    )
    fig.update_geos(
        showcoastlines=False,
        showframe=False,
        showcountries=True,
        countrycolor="#6c757d",
        countrywidth=0.5,
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=560, legend_title_text="Risk Level")
    return fig
