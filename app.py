"""Interactive Streamlit dashboard for Superstore sales performance."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


DATA_FILE = Path(__file__).resolve().parent / "data" / "processed" / "superstore_cleaned.csv"

st.set_page_config(
    page_title="Superstore Sales Performance",
    layout="wide",
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


df = load_data()

st.title("Superstore Sales Performance Analysis")
st.caption(
    "Explore sales, profit, discount, customers, and shipping across the Global Superstore dataset. "
    "Amounts use dataset units; no common currency is specified."
)

st.sidebar.header("Filters")
selected_years = st.sidebar.multiselect(
    "Order year", sorted(df["order_year"].dropna().unique().tolist()),
    default=sorted(df["order_year"].dropna().unique().tolist()),
)
selected_regions = st.sidebar.multiselect(
    "Region", sorted(df["region"].dropna().unique().tolist()),
    default=sorted(df["region"].dropna().unique().tolist()),
)
selected_categories = st.sidebar.multiselect(
    "Category", sorted(df["category"].dropna().unique().tolist()),
    default=sorted(df["category"].dropna().unique().tolist()),
)
selected_segments = st.sidebar.multiselect(
    "Segment", sorted(df["segment"].dropna().unique().tolist()),
    default=sorted(df["segment"].dropna().unique().tolist()),
)

filtered = df[
    df["order_year"].isin(selected_years)
    & df["region"].isin(selected_regions)
    & df["category"].isin(selected_categories)
    & df["segment"].isin(selected_segments)
].copy()

if filtered.empty:
    st.info("No rows match these filters. Select at least one value in each filter.")
    st.stop()

total_sales = filtered["sales"].sum()
total_profit = filtered["profit"].sum()
profit_margin = total_profit / total_sales if total_sales else 0
total_orders = filtered["order_id"].nunique()

st.subheader("Performance at a glance")
kpi_columns = st.columns(4)
kpi_columns[0].metric("Total sales", f"{total_sales:,.0f}")
kpi_columns[1].metric("Total profit", f"{total_profit:,.2f}")
kpi_columns[2].metric("Profit margin", f"{profit_margin:.2%}")
kpi_columns[3].metric("Total orders", f"{total_orders:,}")

st.caption(f"Showing {len(filtered):,} order lines after filters.")

monthly = (
    filtered.groupby(pd.Grouper(key="order_date", freq="MS"))
    .agg(sales=("sales", "sum"), profit=("profit", "sum"))
    .reset_index()
)
trend = make_subplots(specs=[[{"secondary_y": True}]])
trend.add_trace(
    go.Scatter(x=monthly["order_date"], y=monthly["sales"], name="Sales", mode="lines"),
    secondary_y=False,
)
trend.add_trace(
    go.Scatter(x=monthly["order_date"], y=monthly["profit"], name="Profit", mode="lines"),
    secondary_y=True,
)
trend.update_layout(
    title="Monthly Sales and Profit Trend",
    xaxis_title="Order month",
    legend_title="Measure",
    hovermode="x unified",
)
trend.update_yaxes(title_text="Sales (dataset units)", secondary_y=False)
trend.update_yaxes(title_text="Profit (dataset units)", secondary_y=True)
st.plotly_chart(trend, width="stretch")

left, right = st.columns(2)
with left:
    category_summary = (
        filtered.groupby("category")
        .agg(sales=("sales", "sum"), profit=("profit", "sum"))
        .reset_index()
        .melt(id_vars="category", var_name="measure", value_name="amount")
    )
    category_chart = px.bar(
        category_summary,
        x="category",
        y="amount",
        color="measure",
        barmode="group",
        title="Sales and Profit by Category",
        labels={"amount": "Amount (dataset units)", "category": "Category"},
    )
    st.plotly_chart(category_chart, width="stretch")

with right:
    region_summary = (
        filtered.groupby("region", as_index=False)["profit"]
        .sum()
        .sort_values("profit")
    )
    region_chart = px.bar(
        region_summary,
        x="profit",
        y="region",
        orientation="h",
        title="Profit by Region",
        labels={"profit": "Profit (dataset units)", "region": "Region"},
        color="profit",
        color_continuous_scale="RdYlGn",
    )
    st.plotly_chart(region_chart, width="stretch")

state_summary = filtered.groupby("state", as_index=False)["profit"].sum()
state_extremes = pd.concat(
    [state_summary.nsmallest(10, "profit"), state_summary.nlargest(10, "profit")]
).drop_duplicates(subset="state")
state_chart = px.bar(
    state_extremes.sort_values("profit"),
    x="profit",
    y="state",
    orientation="h",
    title="Profit by State / Province (10 Lowest and 10 Highest)",
    labels={"profit": "Profit (dataset units)", "state": "State / Province"},
    color="profit",
    color_continuous_scale="RdYlGn",
)
st.plotly_chart(state_chart, width="stretch")

scatter_data = filtered
if len(scatter_data) > 8000:
    scatter_data = scatter_data.sample(n=8000, random_state=42)
discount_chart = px.scatter(
    scatter_data,
    x="discount",
    y="profit",
    color="category",
    opacity=0.55,
    title="Discount vs Profit (up to 8,000 sampled order lines)",
    labels={"discount": "Discount rate", "profit": "Profit (dataset units)"},
    hover_data=["product_name", "region"],
)
st.plotly_chart(discount_chart, width="stretch")

product_summary = (
    filtered.groupby("product_name", as_index=False)["profit"]
    .sum()
    .nlargest(10, "profit")
    .sort_values("profit")
)
product_chart = px.bar(
    product_summary,
    x="profit",
    y="product_name",
    orientation="h",
    title="Top 10 Products by Profit",
    labels={"profit": "Profit (dataset units)", "product_name": "Product"},
    color="profit",
    color_continuous_scale="Greens",
)
st.plotly_chart(product_chart, width="stretch")

segment_summary = (
    filtered.groupby("segment", as_index=False)
    .agg(sales=("sales", "sum"), profit=("profit", "sum"))
)
segment_chart = px.pie(
    segment_summary,
    names="segment",
    values="sales",
    hole=0.45,
    title="Sales Split by Customer Segment",
    hover_data=["profit"],
)
st.plotly_chart(segment_chart, width="stretch")

st.subheader("Key Insights")
st.caption("The following findings describe the complete dataset, not only the current filter selection.")
st.markdown(
    """
- Total sales were **12,642,905** and total profit was **1,467,457.29**; overall weighted margin was **11.61%**.
- Annual sales increased from **2,259,511 in 2011** to **4,300,041 in 2014**.
- Technology led category profit at **663,778.73**; Tables lost **64,083.39**.
- The 40%+ discount bucket (including exactly 40%) averaged **-76.07** profit per order line, versus **61.04** for no discount.
- The Central region led profit at **311,403.98**; Istanbul had the largest state/province loss at **-29,033.70**.
"""
)
