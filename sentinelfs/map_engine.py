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
        color="risk_level",
        hover_name="country_name",
        hover_data={
            "iso3": True,
            "risk_score": ':.1f',
            "risk_level": True,
            "window": True,
            "commodity_view": True,
    },
    custom_data=["iso3", "country_name"],  # ✅ مهم للكليك
    color_discrete_map={
        "Low": "#2ecc71",
        "Medium": "#f1c40f",
        "High": "#e74c3c",
    },
    projection="natural earth",
)

    fig.update_traces(marker_line_width=0.6, marker_line_color="rgba(255,255,255,0.35)")
    fig.update_geos(showcoastlines=False, showframe=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=560, legend_title_text="")
    return fig
