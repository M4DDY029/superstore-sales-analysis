"""Interactive Streamlit dashboard for Superstore sales performance."""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


DATA_FILE = Path(__file__).resolve().parent / "data" / "processed" / "superstore_cleaned.csv"
INK = "#172923"
GREEN = "#187456"
MINT = "#DDEFE6"
CORAL = "#C7654F"
MUTED = "#718078"
GRID = "#E8EDE9"

st.set_page_config(
    page_title="Superstore | Sales & Profit",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');

    :root {{
        --ink: {INK};
        --green: {GREEN};
        --muted: {MUTED};
        --line: #E5EAE6;
        --paper: #F7F9F7;
    }}
    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
        color: var(--ink);
    }}
    .stApp {{ background: var(--paper); }}
    [data-testid="stHeader"] {{ background: rgba(247,249,247,.92); }}
    [data-testid="stAppViewContainer"] .main .block-container {{
        max-width: 1440px;
        padding: 2rem 3.25rem 4rem;
    }}
    [data-testid="stSidebar"] {{
        background: #F0F4F1;
        border-right: 1px solid var(--line);
    }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: 1.5rem; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: var(--muted);
        font-size: .88rem;
    }}
    h1, h2, h3 {{ color: var(--ink); letter-spacing: -.035em; }}
    h1 {{ font-family: 'DM Serif Display', Georgia, serif; font-weight: 400; }}
    [data-testid="stMetric"] {{
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 1.05rem 1.15rem;
        min-height: 120px;
        box-shadow: 0 2px 8px rgba(23,41,35,.025);
    }}
    [data-testid="stMetricLabel"] p {{
        color: var(--muted);
        font-size: .78rem;
        font-weight: 600;
        letter-spacing: .04em;
        text-transform: uppercase;
    }}
    [data-testid="stMetricValue"] {{
        color: var(--ink);
        font-size: 1.65rem;
        font-weight: 600;
        letter-spacing: -.04em;
    }}
    [data-testid="stPlotlyChart"] {{
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: .5rem .65rem .15rem;
        box-shadow: 0 2px 8px rgba(23,41,35,.025);
    }}
    div[data-testid="stButton"] > button {{
        border: 1px solid #D5DED8;
        border-radius: 8px;
        color: var(--ink);
        background: white;
        font-weight: 600;
    }}
    div[data-testid="stButton"] > button:hover {{
        border-color: var(--green);
        color: var(--green);
    }}
    .eyebrow {{
        color: var(--green);
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .15em;
        text-transform: uppercase;
        margin-bottom: .6rem;
    }}
    .hero {{
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 2rem 2.2rem 1.65rem;
        margin: 0 0 1.6rem;
        box-shadow: 0 4px 16px rgba(23,41,35,.035);
    }}
    .hero h1 {{
        margin: 0;
        font-size: clamp(2.2rem, 4vw, 3.35rem);
        line-height: 1.08;
    }}
    .hero-copy {{
        color: var(--muted);
        font-size: .98rem;
        line-height: 1.65;
        max-width: 780px;
        margin-top: .75rem;
    }}
    .hero-meta {{
        display: flex;
        gap: .55rem;
        flex-wrap: wrap;
        margin-top: 1.25rem;
    }}
    .hero-tag {{
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: .32rem .7rem;
        color: #53645B;
        background: #FAFCFA;
        font-size: .76rem;
        font-weight: 600;
    }}
    .section-heading {{
        display: flex;
        align-items: baseline;
        gap: .7rem;
        margin: 2rem 0 .25rem;
    }}
    .section-heading .number {{
        color: var(--green);
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .1em;
    }}
    .section-heading .title {{
        color: var(--ink);
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: -.035em;
    }}
    .section-note {{
        color: var(--muted);
        font-size: .88rem;
        margin: 0 0 .8rem;
    }}
    .insight-card {{
        height: 100%;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: #FFFFFF;
        padding: 1.1rem 1.2rem;
    }}
    .insight-label {{
        color: var(--green);
        font-size: .7rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: .45rem;
    }}
    .insight-value {{
        color: var(--ink);
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -.035em;
        line-height: 1.25;
    }}
    .insight-detail {{
        color: var(--muted);
        font-size: .83rem;
        line-height: 1.5;
        margin-top: .35rem;
    }}
    .footer-note {{
        color: var(--muted);
        border-top: 1px solid var(--line);
        padding-top: 1rem;
        margin-top: 2rem;
        font-size: .77rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the cleaned project data once and reuse it across interactions."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned data not found at {DATA_FILE}. Run src/clean_data.py first."
        )

    data = pd.read_csv(DATA_FILE, parse_dates=["order_date", "ship_date"])
    required_columns = {
        "sales",
        "profit",
        "order_id",
        "customer_id",
        "order_date",
        "order_year",
        "region",
        "category",
        "segment",
        "state",
        "product_name",
        "discount",
        "ship_mode",
        "shipping_days",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Cleaned data is missing columns: {sorted(missing_columns)}")
    return data


def section_heading(number: str, title: str, note: str) -> None:
    """Render a consistent section title and its short explanation."""
    st.markdown(
        f"""
        <div class="section-heading">
            <span class="number">{number}</span>
            <span class="title">{title}</span>
        </div>
        <div class="section-note">{note}</div>
        """,
        unsafe_allow_html=True,
    )


def style_figure(figure: go.Figure, height: int = 360) -> go.Figure:
    """Apply the shared chart styling while keeping each chart interactive."""
    figure.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=54, b=24),
        font=dict(family="DM Sans, sans-serif", color=INK, size=12),
        title=dict(font=dict(size=15, color=INK), x=0.025, xanchor="left"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text="",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#FFFFFF", font_color=INK),
    )
    figure.update_xaxes(showgrid=True, gridcolor=GRID, zerolinecolor=GRID, title_font_size=11)
    figure.update_yaxes(showgrid=True, gridcolor=GRID, zerolinecolor=GRID, title_font_size=11)
    return figure


df = load_data()
year_options = sorted(int(year) for year in df["order_year"].dropna().unique())
region_options = sorted(df["region"].dropna().unique().tolist())
category_options = sorted(df["category"].dropna().unique().tolist())
segment_options = sorted(df["segment"].dropna().unique().tolist())

st.sidebar.markdown(
    """
    <div style="font-size:.72rem;font-weight:700;letter-spacing:.15em;color:#187456">
    SUPERSTORE / REPORT 01
    </div>
    <div style="font-family:Georgia,serif;font-size:1.55rem;color:#172923;margin:.35rem 0 .3rem">
    Explore the data
    </div>
    <div style="font-size:.83rem;color:#718078;line-height:1.5;margin-bottom:1.3rem">
    Adjust the selections to update every chart and headline metric.
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("Reset all filters", use_container_width=True):
    st.session_state["year_filter"] = year_options
    st.session_state["region_filter"] = region_options
    st.session_state["category_filter"] = category_options
    st.session_state["segment_filter"] = segment_options

selected_years = st.sidebar.multiselect(
    "Order year", year_options, default=year_options, key="year_filter"
)
selected_regions = st.sidebar.multiselect(
    "Region", region_options, default=region_options, key="region_filter"
)
selected_categories = st.sidebar.multiselect(
    "Category", category_options, default=category_options, key="category_filter"
)
selected_segments = st.sidebar.multiselect(
    "Customer segment", segment_options, default=segment_options, key="segment_filter"
)
st.sidebar.divider()
st.sidebar.caption("Source · Global Superstore")
st.sidebar.caption("Period · 2011–2014")
st.sidebar.caption("Amounts · Dataset units; currency not specified")

filtered = df[
    df["order_year"].isin(selected_years)
    & df["region"].isin(selected_regions)
    & df["category"].isin(selected_categories)
    & df["segment"].isin(selected_segments)
].copy()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Commercial performance / 2011—2014</div>
        <h1>Superstore sales,<br>in perspective.</h1>
        <div class="hero-copy">
            A closer look at the products, places and pricing decisions shaping
            sales performance. Use the filters to explore the dataset from
            different business angles.
        </div>
        <div class="hero-meta">
            <span class="hero-tag">Global Superstore</span>
            <span class="hero-tag">51,290 order lines</span>
            <span class="hero-tag">Four years of activity</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.info("No records match these filters. Choose at least one value in every filter.")
    st.stop()

total_sales = filtered["sales"].sum()
total_profit = filtered["profit"].sum()
profit_margin = total_profit / total_sales if total_sales else 0
total_orders = filtered["order_id"].nunique()
total_customers = filtered["customer_id"].nunique()

section_heading(
    "01",
    "The headline numbers",
    "A filtered view of commercial performance. Values are shown in dataset units.",
)
metric_columns = st.columns(4)
for column, label, value in zip(
    metric_columns,
    ["Net sales", "Profit", "Profit margin", "Orders"],
    [f"{total_sales:,.0f}", f"{total_profit:,.0f}", f"{profit_margin:.1%}", f"{total_orders:,}"],
):
    column.metric(label, value)
st.caption(
    f"{len(filtered):,} order lines · {total_customers:,} customers · "
    f"{filtered['order_date'].min():%b %Y} to {filtered['order_date'].max():%b %Y}"
)

monthly = (
    filtered.groupby(pd.Grouper(key="order_date", freq="MS"))
    .agg(sales=("sales", "sum"), profit=("profit", "sum"))
    .reset_index()
)
yearly = filtered.groupby("order_year").agg(sales=("sales", "sum"), profit=("profit", "sum"))
monthly_peaks = monthly.loc[monthly["sales"].idxmax()]
best_year = int(yearly["sales"].idxmax())

section_heading(
    "02",
    "The shape of the business",
    "Monthly sales and profit share a timeline; read the separate axes when comparing scale.",
)
trend = make_subplots(specs=[[{"secondary_y": True}]])
trend.add_trace(
    go.Scatter(
        x=monthly["order_date"],
        y=monthly["sales"],
        name="Sales",
        mode="lines",
        line=dict(color=GREEN, width=2.7),
        fill="tozeroy",
        fillcolor="rgba(24,116,86,.07)",
        hovertemplate="%{x|%b %Y}<br>Sales %{y:,.0f}<extra></extra>",
    ),
    secondary_y=False,
)
trend.add_trace(
    go.Scatter(
        x=monthly["order_date"],
        y=monthly["profit"],
        name="Profit",
        mode="lines",
        line=dict(color=CORAL, width=2.3),
        hovertemplate="%{x|%b %Y}<br>Profit %{y:,.0f}<extra></extra>",
    ),
    secondary_y=True,
)
trend.update_layout(title="Monthly sales and profit", hovermode="x unified")
trend.update_xaxes(title_text="", showgrid=False)
trend.update_yaxes(title_text="Sales · dataset units", secondary_y=False)
trend.update_yaxes(title_text="Profit · dataset units", showgrid=False, secondary_y=True)
st.plotly_chart(style_figure(trend, 390), width="stretch", config={"displayModeBar": False})

insight_cols = st.columns(3)
insights = [
    ("Strongest year", str(best_year), f"Sales of {yearly.loc[best_year, 'sales']:,.0f}"),
    (
        "Largest sales month",
        monthly_peaks["order_date"].strftime("%b %Y"),
        f"Sales of {monthly_peaks['sales']:,.0f}",
    ),
    ("Customers served", f"{total_customers:,}", "Distinct customer IDs in this view"),
]
for column, (label, value, detail) in zip(insight_cols, insights):
    column.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label">{label}</div>
            <div class="insight-value">{value}</div>
            <div class="insight-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

section_heading(
    "03",
    "Where profit comes from",
    "Compare category contribution with regional profit to spot differences in scale and return.",
)
left, right = st.columns(2, gap="large")
category_summary = (
    filtered.groupby("category", as_index=False)
    .agg(sales=("sales", "sum"), profit=("profit", "sum"))
    .sort_values("sales")
)
with left:
    category_chart = go.Figure()
    category_chart.add_trace(
        go.Bar(
            y=category_summary["category"],
            x=category_summary["sales"],
            name="Sales",
            orientation="h",
            marker_color="#A7C9B6",
            hovertemplate="%{y}<br>Sales %{x:,.0f}<extra></extra>",
        )
    )
    category_chart.add_trace(
        go.Bar(
            y=category_summary["category"],
            x=category_summary["profit"],
            name="Profit",
            orientation="h",
            marker_color=GREEN,
            hovertemplate="%{y}<br>Profit %{x:,.0f}<extra></extra>",
        )
    )
    category_chart.update_layout(
        title="Sales and profit by category",
        barmode="group",
        xaxis_title="Dataset units",
        yaxis_title="",
    )
    st.plotly_chart(
        style_figure(category_chart, 350), width="stretch", config={"displayModeBar": False}
    )

with right:
    region_summary = (
        filtered.groupby("region", as_index=False)["profit"]
        .sum()
        .sort_values("profit")
    )
    region_colors = [CORAL if value < 0 else GREEN for value in region_summary["profit"]]
    region_chart = go.Figure(
        go.Bar(
            x=region_summary["profit"],
            y=region_summary["region"],
            orientation="h",
            marker_color=region_colors,
            hovertemplate="%{y}<br>Profit %{x:,.0f}<extra></extra>",
        )
    )
    region_chart.update_layout(
        title="Profit by region",
        xaxis_title="Profit · dataset units",
        yaxis_title="",
        showlegend=False,
    )
    region_chart.add_vline(x=0, line_color="#89958E", line_width=1)
    st.plotly_chart(
        style_figure(region_chart, 350), width="stretch", config={"displayModeBar": False}
    )

section_heading(
    "04",
    "Products & local markets",
    "A ranked look at products and state/province profit. Red bars indicate a net loss.",
)
left, right = st.columns(2, gap="large")
product_summary = (
    filtered.groupby("product_name", as_index=False)["profit"]
    .sum()
    .nlargest(10, "profit")
    .sort_values("profit")
)
with left:
    product_chart = go.Figure(
        go.Bar(
            x=product_summary["profit"],
            y=product_summary["product_name"],
            orientation="h",
            marker_color=GREEN,
            hovertemplate="%{y}<br>Profit %{x:,.0f}<extra></extra>",
        )
    )
    product_chart.update_layout(
        title="Ten most profitable products",
        xaxis_title="Profit · dataset units",
        yaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(
        style_figure(product_chart, 430), width="stretch", config={"displayModeBar": False}
    )

with right:
    state_summary = filtered.groupby("state", as_index=False)["profit"].sum()
    state_extremes = pd.concat(
        [state_summary.nsmallest(8, "profit"), state_summary.nlargest(8, "profit")]
    ).drop_duplicates(subset="state").sort_values("profit")
    state_chart = go.Figure(
        go.Bar(
            x=state_extremes["profit"],
            y=state_extremes["state"],
            orientation="h",
            marker_color=[CORAL if value < 0 else "#75A98D" for value in state_extremes["profit"]],
            hovertemplate="%{y}<br>Profit %{x:,.0f}<extra></extra>",
        )
    )
    state_chart.update_layout(
        title="Highest and lowest profit states / provinces",
        xaxis_title="Profit · dataset units",
        yaxis_title="",
        showlegend=False,
    )
    state_chart.add_vline(x=0, line_color="#89958E", line_width=1)
    st.plotly_chart(
        style_figure(state_chart, 430), width="stretch", config={"displayModeBar": False}
    )

section_heading(
    "05",
    "Price, customers & fulfilment",
    "Discount is shown at order-line level. Patterns are descriptive, not proof of cause and effect.",
)
left, right = st.columns(2, gap="large")
scatter_data = filtered
if len(scatter_data) > 8000:
    scatter_data = scatter_data.sample(n=8000, random_state=42)
with left:
    discount_chart = px.scatter(
        scatter_data,
        x="discount",
        y="profit",
        color="category",
        opacity=0.48,
        hover_data=["product_name", "region"],
        labels={"discount": "Discount rate", "profit": "Profit · dataset units"},
        color_discrete_sequence=[GREEN, "#D39B4D", "#7697A8"],
    )
    discount_chart.add_hline(y=0, line_dash="dot", line_color=CORAL, line_width=1.5)
    discount_chart.update_xaxes(tickformat=".0%")
    discount_chart.update_layout(
        title="Discount and profit by order line",
        xaxis_title="Discount",
        yaxis_title="Profit · dataset units",
    )
    st.plotly_chart(
        style_figure(discount_chart, 390), width="stretch", config={"displayModeBar": False}
    )

discount_conditions = [
    filtered["discount"].eq(0),
    filtered["discount"].le(0.20),
    filtered["discount"].lt(0.40),
]
filtered["discount_bucket"] = np.select(
    discount_conditions,
    ["0%", "1–20%", ">20–<40%"],
    default="40%+",
)
bucket_order = ["0%", "1–20%", ">20–<40%", "40%+"]
discount_summary = (
    filtered.groupby("discount_bucket", as_index=False, observed=False)
    .agg(average_profit=("profit", "mean"), rows=("profit", "size"))
    .set_index("discount_bucket")
    .reindex(bucket_order)
    .dropna(subset=["average_profit"])
    .reset_index()
)
with right:
    discount_bucket_chart = go.Figure(
        go.Bar(
            x=discount_summary["discount_bucket"],
            y=discount_summary["average_profit"],
            marker_color=[
                CORAL if value < 0 else GREEN
                for value in discount_summary["average_profit"]
            ],
            customdata=discount_summary["rows"],
            hovertemplate=(
                "%{x}<br>Average profit %{y:,.2f}<br>"
                "Order lines %{customdata:,}<extra></extra>"
            ),
        )
    )
    discount_bucket_chart.add_hline(y=0, line_color="#89958E", line_width=1)
    discount_bucket_chart.update_layout(
        title="Average profit by discount band",
        xaxis_title="Discount band",
        yaxis_title="Average profit · dataset units",
        showlegend=False,
    )
    st.plotly_chart(
        style_figure(discount_bucket_chart, 390),
        width="stretch",
        config={"displayModeBar": False},
    )

left, right = st.columns(2, gap="large")
segment_summary = (
    filtered.groupby("segment", as_index=False)
    .agg(sales=("sales", "sum"), profit=("profit", "sum"))
    .sort_values("sales")
)
with left:
    segment_chart = go.Figure()
    segment_chart.add_trace(
        go.Bar(
            x=segment_summary["segment"],
            y=segment_summary["sales"],
            name="Sales",
            marker_color="#A7C9B6",
            hovertemplate="%{x}<br>Sales %{y:,.0f}<extra></extra>",
        )
    )
    segment_chart.add_trace(
        go.Bar(
            x=segment_summary["segment"],
            y=segment_summary["profit"],
            name="Profit",
            marker_color=GREEN,
            hovertemplate="%{x}<br>Profit %{y:,.0f}<extra></extra>",
        )
    )
    segment_chart.update_layout(
        title="Sales and profit by customer segment",
        barmode="group",
        xaxis_title="",
        yaxis_title="Dataset units",
    )
    st.plotly_chart(
        style_figure(segment_chart, 350), width="stretch", config={"displayModeBar": False}
    )

with right:
    shipping_summary = (
        filtered.groupby("ship_mode", as_index=False)
        .agg(average_days=("shipping_days", "mean"), orders=("order_id", "nunique"))
        .sort_values("average_days")
    )
    shipping_chart = go.Figure(
        go.Bar(
            x=shipping_summary["average_days"],
            y=shipping_summary["ship_mode"],
            orientation="h",
            marker_color="#6E9E85",
            customdata=shipping_summary["orders"],
            hovertemplate=(
                "%{y}<br>Average %{x:.2f} days<br>"
                "Orders %{customdata:,}<extra></extra>"
            ),
        )
    )
    shipping_chart.update_layout(
        title="Average fulfilment time by ship mode",
        xaxis_title="Elapsed calendar days",
        yaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(
        style_figure(shipping_chart, 350), width="stretch", config={"displayModeBar": False}
    )

st.markdown(
    """
    <div class="footer-note">
        Source: Global Superstore · 51,290 order lines · 2011–2014.
        Amounts are reported in source units; the dataset does not identify a common currency.
        Discount-profit patterns are descriptive and should not be interpreted as causal.
    </div>
    """,
    unsafe_allow_html=True,
)
