import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

from db_connect import query_df

# Pull the primary dashboard table directly from the governed dbt mart —
# the same table Part 7's analysis queries and dbt's tests both run against.
df = query_df("SELECT * FROM housing_dbt.housing_pulse_marts.city_price_trends")
df["year_month"] = pd.to_datetime(df["year_month"])

# Key cities to highlight
HIGHLIGHT_CITIES = [
    "Toronto", "Vancouver", "Calgary", "Edmonton",
    "Montreal", "Ottawa-Gatineau", "Halifax", "Winnipeg", "Saskatoon"
]
CITY_COLORS = {
    "Toronto": "#e63946",
    "Vancouver": "#457b9d",
    "Calgary": "#f4a261",
    "Edmonton": "#2a9d8f",
    "Montreal": "#8338ec",
    "Ottawa-Gatineau": "#06d6a0",
    "Halifax": "#fb8500",
    "Winnipeg": "#023047",
    "Canada (National)": "#adb5bd",
}

def chart_price_trends(df):
    fig = go.Figure()
    cities_to_plot = HIGHLIGHT_CITIES + ["Canada (National)"]

    for city in cities_to_plot:
        city_df = df[df["city"] == city].sort_values("year_month")
        if city_df.empty:
            continue
        is_national = city == "Canada (National)"
        fig.add_trace(go.Scatter(
            x=city_df["year_month"],
            y=city_df["index_value"],
            name=city,
            line=dict(
            color=CITY_COLORS.get(city, "#888"),
            width=1.5 if is_national else 2,
            dash="dash" if is_national else "solid",
        ),
        opacity=0.6 if is_national else 1.0,
        hovertemplate=(
            f"<b>{city}</b><br>"
            "Date: %{x|%b %Y}<br>"
            "Index: %{y:.1f}<br>"
            "<extra></extra>"
        )
        ))
    fig.add_hline(
        y=100, line_dash="dot", line_color="#6c757d", line_width=1,
        annotation_text="Dec 2016 baseline (=100)",
        annotation_position="bottom right",
    )
    fig.add_vrect(
        x0="2020-03-01", x1="2022-06-01",
        fillcolor="rgba(255,200,0,0.08)",
        layer="below", line_width=0,
        annotation_text="COVID boom",
        annotation_position="top left",
    )
    fig.update_layout(
        title=dict(
            text="<b>Canada New Housing Price Index by City</b>"
            "<br><sup>Base: December 2016 = 100 | Source: Statistics Canada, via dbt mart</sup>",
            font=dict(size=18),
        ),
        xaxis_title="Date",
        yaxis_title="Housing Price Index",
        legend=dict(orientation="v", x=1.01, y=1),
        hovermode="x unified",
        height=520,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=12),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        margin=dict(l=60, r=160, t=80, b=60),
    )
    return fig

def chart_yoy_heatmap(df):
    """
    Creates a Plotly heatmap visualizing Year-over-Year price changes by city.
    """
    # Prepare the data
    heat_df = (
        df[df["city"].isin(HIGHLIGHT_CITIES)]
        .groupby(["city", "year"])["yoy_change_pct"]
        .mean()
        .reset_index()
        .pivot(index="city", columns="year", values="yoy_change_pct")
    )
    
    # Filter for years 2010 onwards
    heat_df = heat_df[[c for c in heat_df.columns if c >= 2010]]

    # Configure heatmap trace
    fig = go.Figure(
        data=go.Heatmap(
            z=heat_df.values,
            x=[str(c) for c in heat_df.columns],
            y=heat_df.index.tolist(),
            colorscale=[
                [0.0, "#d62828"],
                [0.35, "#f77f00"],
                [0.5, "#ffffff"],
                [0.65, "#80b918"],
                [1.0, "#1a6b1e"],
            ],
            zmid=0,
            text=heat_df.values.round(1),
            texttemplate="%{text}%",
            textfont=dict(size=9),
            hoverongaps=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Year: %{x}<br>"
                "Avg YoY: %{z:.1f}%<br>"
                "<extra></extra>"
            ),
            colorbar=dict(title="Avg YoY<br>Change (%)", ticksuffix="%"),
        )
    )

    # Update layout aesthetics
    fig.update_layout(
        title=dict(
            text=(
                "<b>Year-over-Year Price Change by City</b>"
                "<br><sup>Average annual % change | Red = falling, Green = rising</sup>"
            ),
            font=dict(size=18),
        ),
        xaxis_title="Year",
        yaxis_title="City",
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=12),
        margin=dict(l=140, r=80, t=80, b=60),
    )

    return fig



def chart_inflection_points(df):
    """
    Creates a bar chart visualizing when each city's housing index first crossed 150.
    """
    # Prepare the data
    inflection = (
        df[df["index_value"] >= 150]
        .groupby("city")["year_month"]
        .min()
        .reset_index()
        .rename(columns={"year_month": "first_crossed_150"})
    )
    
    # Filter by highlighted cities and sort
    inflection = inflection[
        inflection["city"].isin(HIGHLIGHT_CITIES)
    ].sort_values("first_crossed_150")
    
    inflection["label"] = inflection["first_crossed_150"].dt.strftime("%b %Y")
    
    # Configure bar chart trace
    fig = go.Figure(
        go.Bar(
            x=inflection["city"],
            y=inflection["first_crossed_150"].dt.year + inflection["first_crossed_150"].dt.month / 12,
            text=inflection["label"],
            textposition="outside",
            marker_color=[CITY_COLORS.get(c, "#888") for c in inflection["city"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "First crossed 150: %{text}<br>"
                "<extra></extra>"
            ),
        )
    )
    
    # Update layout aesthetics
    fig.update_layout(
        title=dict(
            text=(
                "<b>When Did Each City's Housing Index Cross 150?</b>"
                "<br><sup>First month prices hit 50% above December 2016 baseline</sup>"
            ),
            font=dict(size=18),
        ),
        xaxis_title="City",
        yaxis_title="Year",
        height=440,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#f0f0f0", 
            range=[2015, 2025], 
            tickformat="d"
        ),
        margin=dict(l=60, r=60, t=80, b=80),
        showlegend=False,
    )
    
    return fig


def chart_recovery(df):
    """
    Creates a horizontal bar chart visualizing the recovery status (percentage below peak) by city.
    """
    # Prepare the data
    latest = df.sort_values("year_month").groupby("city").last().reset_index()
    latest = latest[latest["city"].isin(HIGHLIGHT_CITIES)].copy()
    latest = latest.sort_values("pct_below_peak", ascending=True)
    
    # Define colors: Blue if recovery is > 5% below peak, Red otherwise
    colors = ["#457b9d" if v < -5 else "#e63946" for v in latest["pct_below_peak"]]
    
    # Configure bar chart trace
    fig = go.Figure(
        go.Bar(
            x=latest["pct_below_peak"],
            y=latest["city"],
            orientation="h",
            text=[f"{v:.1f}%" for v in latest["pct_below_peak"]],
            textposition="outside",
            marker_color=colors,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "% below peak: %{x:.1f}%<br>"
                "<extra></extra>"
            ),
        )
    )
    
    # Add vertical threshold lines
    fig.add_vline(x=0, line_color="#333", line_width=1)
    fig.add_vline(
        x=-5, 
        line_dash="dot", 
        line_color="#888", 
        line_width=1,
        annotation_text="Recovery threshold", 
        annotation_position="top"
    )
    
    # Update layout aesthetics
    fig.update_layout(
        title=dict(
            text=(
                "<b>How Far Is Each City From Its Peak?</b>"
                "<br><sup>Blue = recovering (>5% below peak), Red = still near peak</sup>"
            ),
            font=dict(size=18),
        ),
        xaxis_title="% Below All-Time Peak",
        yaxis_title="",
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=12),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0", ticksuffix="%"),
        yaxis=dict(showgrid=False),
        margin=dict(l=140, r=100, t=80, b=60),
        showlegend=False,
    )
    
    return fig

def build_dashboard(df):
    """
    Constructs an HTML dashboard using Plotly charts and saves it to a file.
    """
    # Generate the individual charts
    fig1 = chart_price_trends(df)
    fig2 = chart_yoy_heatmap(df)
    fig3 = chart_inflection_points(df)
    fig4 = chart_recovery(df)

    html_parts = []
    
    # HTML template structure
    html_parts.append("""
    <html>
    <head>
    <meta charset="utf-8">
    <title>Canada Housing Pulse Dashboard</title>
    <style>
        body { font-family: Inter, Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }
        h1 { color: #1a1a2e; font-size: 28px; margin-bottom: 4px; }
        p.subtitle { color: #6c757d; font-size: 14px; margin-top: 0; margin-bottom: 30px; }
        .chart-container {
            background: white; 
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            padding: 10px; 
            margin-bottom: 24px;
        }
    </style>
    </head>
    <body>
        <h1>CanadaHousingPulse</h1>
        <p class="subtitle">
            40+ years of Statistics Canada New Housing Price Index data |
            27 Canadian cities | Sourced live from dbt-tested Databricks marts |
            Built with Python, Databricks, dbt &amp; Plotly
        </p>
    """)

    # Append each chart to the HTML
    figs = [fig1, fig2, fig3, fig4]
    for i, fig in enumerate(figs):
        # Include Plotly JS only for the first chart to optimize loading
        chart_html = fig.to_html(
            full_html=False,
            include_plotlyjs="cdn" if i == 0 else False,
        )
        html_parts.append(f'<div class="chart-container">{chart_html}</div>')

    html_parts.append("</body></html>")


    output_path = "dashboard/housing_pulse.html"
    # Write the dashboard file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))
    
    print(f"Dashboard saved -> {output_path}")
    print("Open it in your browser: just double-click the file")

if __name__ == "__main__":
    # Ensure build_dashboard is called with a valid dataframe
    build_dashboard(df)
