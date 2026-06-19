"""
Superstore Sales Dashboard
A modern, interactive Streamlit dashboard for the Sample Superstore dataset.

Run with:
    streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# MODERN STYLING (dark theme, gradient KPI cards, clean fonts)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f1117 0%, #161a23 100%);
    }
    h1, h2, h3, h4, h5, p, span, label, div { color: #eaeaf0; }

    /* Title banner */
    .dashboard-title {
        background: linear-gradient(90deg, #6a3ef5 0%, #b03ef5 50%, #f53e9a 100%);
        padding: 22px 30px;
        border-radius: 16px;
        margin-bottom: 22px;
        box-shadow: 0 4px 20px rgba(176, 62, 245, 0.25);
    }
    .dashboard-title h1 {
        color: white;
        font-size: 30px;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin: 0;
    }
    .dashboard-title p {
        color: rgba(255,255,255,0.85);
        margin: 4px 0 0 0;
        font-size: 14px;
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(145deg, #1d2130 0%, #262b3d 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 18px 20px;
        text-align: left;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        height: 100%;
    }
    .kpi-label {
        font-size: 13px;
        color: #9aa0b4;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 2px;
    }
    .kpi-delta-pos { color: #3ddc97; font-size: 13px; font-weight: 600; }
    .kpi-delta-neg { color: #ff5c7a; font-size: 13px; font-weight: 600; }

    /* Section card wrapper for charts */
    .chart-card {
        background: #1a1e29;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 14px 16px 4px 16px;
        margin-bottom: 18px;
    }
    .chart-title {
        font-size: 15px;
        font-weight: 700;
        color: #eaeaf0;
        margin-bottom: 4px;
    }

    section[data-testid="stSidebar"] {
        background: #11141d;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* ---- Multiselect: input box ---- */
    div[data-baseweb="select"] > div {
        background-color: #1d2130;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.10);
    }

    /* Cap the height of the selected-tags box so it doesn't grow huge,
       and let it scroll internally instead of pushing the dropdown panel down */
    div[data-baseweb="select"] > div:first-child {
        max-height: 120px;
        overflow-y: auto;
    }

    /* Selected option "pills" */
    span[data-baseweb="tag"] {
        background-color: #6a3ef5 !important;
        border-radius: 6px !important;
        margin: 2px !important;
    }

    /* ---- Dropdown menu (the floating list with options / "No results") ---- */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"] {
        background-color: #1d2130 !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="popover"] ul li,
    div[data-baseweb="menu"] li {
        background-color: #1d2130 !important;
        color: #eaeaf0 !important;
    }
    div[data-baseweb="popover"] ul li:hover,
    div[data-baseweb="menu"] li:hover {
        background-color: #2a2f42 !important;
    }
    /* "No results" / empty-state text inside the dropdown */
    div[data-baseweb="popover"] div,
    div[data-baseweb="popover"] span {
        color: #eaeaf0;
    }

    /* Sidebar multiselect labels need breathing room above each widget */
    section[data-testid="stSidebar"] label {
        font-weight: 600;
        margin-bottom: 4px;
    }

    /* Keep dropdown panel from getting clipped by sidebar overflow */
    section[data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] > div:first-child {
        overflow: visible;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_TEMPLATE = "plotly_dark"
ACCENT_SEQ = ["#6a3ef5", "#b03ef5", "#f53e9a", "#3ddc97", "#39c0ff", "#ffb84d"]


# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path: str = "Sample_-_Superstore.csv") -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin1")

    def parse_mixed_date(s: str):
        try:
            return pd.to_datetime(s, format="%d-%m-%Y")
        except (ValueError, TypeError):
            try:
                return pd.to_datetime(s, format="%m/%d/%Y")
            except (ValueError, TypeError):
                return pd.to_datetime(s, errors="coerce")

    df["Order Date"] = df["Order Date"].apply(parse_mixed_date)
    df["Ship Date"] = df["Ship Date"].apply(parse_mixed_date)

    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.month
    df["Order Month Name"] = df["Order Date"].dt.strftime("%b")
    df["Order Year-Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Profit Margin"] = (df["Profit"] / df["Sales"]).replace([float("inf"), -float("inf")], 0)

    return df


df_raw = load_data()

# ----------------------------------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 🔎 Filters")
st.sidebar.caption("Leave a filter empty to include all values. Charts and KPIs update live.")

min_date, max_date = df_raw["Order Date"].min(), df_raw["Order Date"].max()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date(),
)

all_regions = sorted(df_raw["Region"].unique())
all_categories = sorted(df_raw["Category"].unique())
all_segments = sorted(df_raw["Segment"].unique())
all_ship_modes = sorted(df_raw["Ship Mode"].unique())
all_states = sorted(df_raw["State"].unique())

regions = st.sidebar.multiselect(
    "Region",
    options=all_regions,
    default=[],
    placeholder="All regions",
)

categories = st.sidebar.multiselect(
    "Category",
    options=all_categories,
    default=[],
    placeholder="All categories",
)

sub_cat_pool = df_raw[df_raw["Category"].isin(categories)] if categories else df_raw
sub_cat_options = sorted(sub_cat_pool["Sub-Category"].unique())
sub_categories = st.sidebar.multiselect(
    "Sub-Category",
    options=sub_cat_options,
    default=[],
    placeholder="All sub-categories",
)

segments = st.sidebar.multiselect(
    "Customer Segment",
    options=all_segments,
    default=[],
    placeholder="All segments",
)

ship_modes = st.sidebar.multiselect(
    "Ship Mode",
    options=all_ship_modes,
    default=[],
    placeholder="All ship modes",
)

states = st.sidebar.multiselect(
    "State",
    options=all_states,
    default=[],
    placeholder="All states",
)

st.sidebar.markdown("---")
reset = st.sidebar.button("🔄 Reset all filters", use_container_width=True)
if reset:
    st.rerun()

# ----------------------------------------------------------------------------
# APPLY FILTERS
# (An empty selection means "no filter" — i.e. include every value)
# ----------------------------------------------------------------------------
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date.date(), max_date.date()

mask = (
    (df_raw["Order Date"].dt.date >= start_date)
    & (df_raw["Order Date"].dt.date <= end_date)
    & (df_raw["Region"].isin(regions) if regions else True)
    & (df_raw["Category"].isin(categories) if categories else True)
    & (df_raw["Sub-Category"].isin(sub_categories) if sub_categories else True)
    & (df_raw["Segment"].isin(segments) if segments else True)
    & (df_raw["Ship Mode"].isin(ship_modes) if ship_modes else True)
)
if states:
    mask &= df_raw["State"].isin(states)

df = df_raw[mask].copy()

# ----------------------------------------------------------------------------
# TITLE
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="dashboard-title">
        <h1>🛒 SUPERSTORE SALES DASHBOARD</h1>
        <p>Interactive overview of sales, profit, and orders across regions, categories &amp; time</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("No data matches the selected filters. Try widening your filter selection.")
    st.stop()

# ----------------------------------------------------------------------------
# KPI CALCULATIONS
# ----------------------------------------------------------------------------
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_orders = df["Order ID"].nunique()
total_quantity = df["Quantity"].sum()
avg_discount = df["Discount"].mean()
profit_margin = (total_profit / total_sales * 100) if total_sales else 0


def fmt_money(x: float) -> str:
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:,.2f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:,.1f}K"
    return f"${x:,.0f}"


kpi_cols = st.columns(5)
kpi_data = [
    ("💰 Total Sales", fmt_money(total_sales)),
    ("📈 Total Profit", fmt_money(total_profit)),
    ("🧾 Total Orders", f"{total_orders:,}"),
    ("📦 Units Sold", f"{int(total_quantity):,}"),
    ("🎯 Profit Margin", f"{profit_margin:.1f}%"),
]
for col, (label, value) in zip(kpi_cols, kpi_data):
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# ROW 1 — Monthly Sales Trend (full width)
# ----------------------------------------------------------------------------
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">📅 Monthly Sales &amp; Profit Trend</div>', unsafe_allow_html=True)

trend = (
    df.groupby("Order Year-Month")[["Sales", "Profit"]]
    .sum()
    .reset_index()
    .sort_values("Order Year-Month")
)

fig_trend = go.Figure()
fig_trend.add_trace(
    go.Scatter(
        x=trend["Order Year-Month"], y=trend["Sales"],
        name="Sales", mode="lines+markers",
        line=dict(color="#b03ef5", width=3),
        fill="tozeroy", fillcolor="rgba(176,62,245,0.12)",
    )
)
fig_trend.add_trace(
    go.Scatter(
        x=trend["Order Year-Month"], y=trend["Profit"],
        name="Profit", mode="lines+markers",
        line=dict(color="#3ddc97", width=3),
        yaxis="y2",
    )
)
fig_trend.update_layout(
    template=PLOTLY_TEMPLATE,
    height=340,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(title=None, showgrid=False),
    yaxis=dict(title="Sales ($)", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
    yaxis2=dict(title="Profit ($)", overlaying="y", side="right", showgrid=False),
)
st.plotly_chart(fig_trend, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# ROW 2 — Category-wise & Region-wise
# ----------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🗂️ Category-wise Sales</div>', unsafe_allow_html=True)
    cat_sales = df.groupby("Category")["Sales"].sum().reset_index().sort_values("Sales", ascending=True)
    fig_cat = px.bar(
        cat_sales, x="Sales", y="Category", orientation="h",
        color="Category", color_discrete_sequence=ACCENT_SEQ, text="Sales",
    )
    fig_cat.update_traces(texttemplate="$%{x:,.0f}", textposition="outside")
    fig_cat.update_layout(
        template=PLOTLY_TEMPLATE, height=300, showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=None), yaxis=dict(title=None),
    )
    st.plotly_chart(fig_cat, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🌎 Region-wise Sales</div>', unsafe_allow_html=True)
    reg_sales = df.groupby("Region")["Sales"].sum().reset_index().sort_values("Sales", ascending=False)
    fig_reg = px.pie(
        reg_sales, names="Region", values="Sales", hole=0.55,
        color_discrete_sequence=ACCENT_SEQ,
    )
    fig_reg.update_traces(textinfo="percent+label", textfont_size=12)
    fig_reg.update_layout(
        template=PLOTLY_TEMPLATE, height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )
    st.plotly_chart(fig_reg, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# ROW 3 — Top Products & Sub-Category Breakdown
# ----------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🏆 Top 10 Products by Sales</div>', unsafe_allow_html=True)
    top_products = (
        df.groupby("Product Name")["Sales"].sum()
        .reset_index().sort_values("Sales", ascending=False).head(10)
    )
    top_products["Product Short"] = top_products["Product Name"].str.slice(0, 35) + top_products["Product Name"].str.len().gt(35).map({True: "…", False: ""})
    fig_top = px.bar(
        top_products.sort_values("Sales"), x="Sales", y="Product Short", orientation="h",
        color="Sales", color_continuous_scale=["#3a2a6e", "#b03ef5", "#f53e9a"],
    )
    fig_top.update_layout(
        template=PLOTLY_TEMPLATE, height=380, showlegend=False, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Sales ($)", showgrid=False), yaxis=dict(title=None),
    )
    st.plotly_chart(fig_top, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📊 Sales by Sub-Category</div>', unsafe_allow_html=True)
    subcat_sales = (
        df.groupby(["Category", "Sub-Category"])["Sales"].sum()
        .reset_index().sort_values("Sales", ascending=False)
    )
    fig_sub = px.treemap(
        subcat_sales, path=["Category", "Sub-Category"], values="Sales",
        color="Sales", color_continuous_scale=["#1d2130", "#6a3ef5", "#f53e9a"],
    )
    fig_sub.update_layout(
        template=PLOTLY_TEMPLATE, height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_sub, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# ROW 4 — Segment performance & Discount vs Profit
# ----------------------------------------------------------------------------
c5, c6 = st.columns(2)

with c5:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">👥 Sales by Customer Segment</div>', unsafe_allow_html=True)
    seg_sales = df.groupby("Segment")[["Sales", "Profit"]].sum().reset_index()
    fig_seg = go.Figure()
    fig_seg.add_trace(go.Bar(name="Sales", x=seg_sales["Segment"], y=seg_sales["Sales"], marker_color="#6a3ef5"))
    fig_seg.add_trace(go.Bar(name="Profit", x=seg_sales["Segment"], y=seg_sales["Profit"], marker_color="#3ddc97"))
    fig_seg.update_layout(
        template=PLOTLY_TEMPLATE, height=320, barmode="group",
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", title=None),
    )
    st.plotly_chart(fig_seg, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c6:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">💸 Discount vs Profit (by Sub-Category)</div>', unsafe_allow_html=True)
    disc_profit = (
        df.groupby("Sub-Category")
        .agg(Discount=("Discount", "mean"), Profit=("Profit", "sum"), Sales=("Sales", "sum"))
        .reset_index()
    )
    fig_dp = px.scatter(
        disc_profit, x="Discount", y="Profit", size="Sales", color="Sub-Category",
        color_discrete_sequence=ACCENT_SEQ + px.colors.qualitative.Set2,
        hover_name="Sub-Category",
    )
    fig_dp.update_layout(
        template=PLOTLY_TEMPLATE, height=320, showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Avg Discount", tickformat=".0%", showgrid=False),
        yaxis=dict(title="Total Profit ($)", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
    )
    st.plotly_chart(fig_dp, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# ROW 5 — Raw data explorer
# ----------------------------------------------------------------------------
with st.expander("🔍 View filtered raw data"):
    st.dataframe(
        df[
            ["Order Date", "Order ID", "Customer Name", "Segment", "Region", "State",
             "Category", "Sub-Category", "Product Name", "Sales", "Quantity", "Discount", "Profit"]
        ].sort_values("Order Date", ascending=False),
        use_container_width=True,
        height=320,
    )
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_superstore_data.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown(
    "<p style='text-align:center; color:#5a5f72; font-size:12px; margin-top:10px;'>"
    "Superstore Sales Dashboard · Built with Streamlit &amp; Plotly</p>",
    unsafe_allow_html=True,
)