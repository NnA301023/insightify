import calendar
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from typing import Tuple
from millify import millify
import plotly.graph_objects as go


# Constants
PAGE_CONFIG = {
    "page_title": "Insightify Dashboard",
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

CUSTOM_COLORS = {
    'Furniture': '#005C53',
    'Office Supplies': '#9FC131',
    'Technology': '#042940'
}

MONTHS = list(calendar.month_abbr)[1:]

# Data Loading
@st.cache_data(ttl=3600)
def load_data() -> Tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """Load and preprocess the dataset."""
    df = pd.read_excel('dataset/superstore_enriched.xlsx')
    df['year'] = pd.to_datetime(df['Order Date']).dt.year
    df['days to ship'] = abs(pd.to_datetime(df['Ship Date']) - pd.to_datetime(df['Order Date'])).dt.days
    
    return (
        df,
        get_per_year_change('Sales', df, 'sum'),
        get_per_year_change('Profit', df, 'sum'),
        get_per_year_change('Order ID', df, 'count')
    )

def get_per_year_change(col: str, df: pd.DataFrame, metric: str) -> pd.Series:
    """Calculate percentage change for a column by year."""
    grp_years = df.groupby('year')[col].agg([metric])[metric]
    grp_years = grp_years.pct_change() * 100
    grp_years.fillna(0, inplace=True)
    return grp_years.apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else 'NaN')

# UI Styling
def set_page_style():
    """Set custom page styling."""
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

def style_metric_cards(
    color: str = "#232323",
    background_color: str = "#FFF",
    border_size_px: int = 1,
    border_color: str = "#CCC",
    border_radius_px: int = 5,
    border_left_color: str = "#9AD8E1",
    box_shadow: bool = True
):
    """Style the metric cards in the dashboard."""
    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        if box_shadow else "box-shadow: none !important;"
    )
    
    st.markdown(
        f"""
        <style>
            div[data-testid="metric-container"] {{
                background-color: {background_color};
                border: {border_size_px}px solid {border_color};
                padding: 5% 5% 5% 10%;
                border-radius: {border_radius_px}px;
                border-left: 0.5rem solid {border_left_color} !important;
                color: {color};
                {box_shadow_str}
            }}
            div[data-testid="metric-container"] p {{
                color: {color};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Dashboard Components
def create_header():
    """Create dashboard header."""
    st.write("")
    st.markdown("<h2 style='text-align: center;'>Superstore Sales</h2>", unsafe_allow_html=True)
    st.write("")

def create_sidebar(df: pd.DataFrame) -> int:
    """Create sidebar with year filter."""
    year_list = sorted(df['year'].unique().tolist())
    year_list.insert(0, "All")
    return st.sidebar.selectbox("Select a year", year_list)

def filter_data(df: pd.DataFrame, selected_year: str) -> pd.DataFrame:
    """Filter dataframe based on selected year."""
    if selected_year != "All":
        return df[df['year'] == int(selected_year)]
    return df

def create_kpi_metrics(
    df: pd.DataFrame,
    grp_years_sales: pd.Series,
    grp_year_profit: pd.Series,
    grp_year_orders: pd.Series,
    selected_year: str
):
    """Create KPI metrics section."""
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_orders = df['Order ID'].nunique()
    
    if selected_year == "All":
        sales_change = grp_years_sales.iloc[-1]
        profit_change = grp_year_profit.iloc[-1]
        orders_change = grp_year_orders.iloc[-1]
    else:
        sales_change = grp_years_sales.get(selected_year, "0%")
        profit_change = grp_year_profit.get(selected_year, "0%")
        orders_change = grp_year_orders.get(selected_year, "0%")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Sales", f"${millify(total_sales, precision=2)}", sales_change)
    col2.metric("Profit", f"${millify(total_profit, precision=2)}", profit_change)
    col3.metric("Orders", total_orders, orders_change)
    
    style_metric_cards(border_left_color="#DBF227")

def create_category_performance_chart(df: pd.DataFrame):
    """Create a scatter plot showing Sales vs Profit by Category."""
    category_perf = df.groupby('Category').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'count'
    }).reset_index()
    
    fig = go.Figure()
    
    for category in category_perf['Category']:
        cat_data = category_perf[category_perf['Category'] == category]
        fig.add_trace(go.Scatter(
            x=[cat_data['Sales'].iloc[0]],
            y=[cat_data['Profit'].iloc[0]],
            mode='markers+text',
            name=category,
            marker=dict(size=cat_data['Order ID'] / 50, color=CUSTOM_COLORS[category]),
            text=[category],
            textposition="top center"
        ))
    
    fig.update_layout(
        title="Category Performance: Sales vs Profit",
        xaxis_title="Sales ($)",
        yaxis_title="Profit ($)",
        height=400
    )
    
    return fig

def create_order_distribution_chart(df: pd.DataFrame):
    """Create a sunburst chart showing order distribution by Region and Segment."""
    order_dist = df.groupby(['Region', 'Segment']).size().reset_index(name='Count')
    color_palette = {
        'West': '#005C53',
        'East': '#9FC131',
        'Central': '#DBF227',
        'South': '#D6FF79'
    }
    labels, parents, values, colors = [], [], [], []
    for region in order_dist['Region'].unique():
        labels.append(region)
        parents.append("")
        region_total = order_dist[order_dist['Region'] == region]['Count'].sum()
        values.append(region_total)
        colors.append(color_palette[region])
    
    for _, row in order_dist.iterrows():
        labels.append(f"{row['Region']} - {row['Segment']}")
        parents.append(row['Region'])
        values.append(row['Count'])
        region_color = color_palette[row['Region']]
        colors.append(f"rgba{tuple(int(region_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.7,)}")
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colors=colors)
    ))
    
    fig.update_layout(
        title="Order Distribution by Region and Segment",
        height=500,
        width=None
    )
    
    return fig

def create_monthly_sales_trend(df: pd.DataFrame):
    """Create a line chart showing monthly sales trends."""
    color_palette = {
        2020: '#005C53',
        2021: '#9FC131',
        2022: '#DBF227',
        2023: '#D6FF79'
    }
    
    df['Month'] = pd.to_datetime(df['Order Date']).dt.strftime('%b')
    df['Month_num'] = pd.to_datetime(df['Order Date']).dt.month
    monthly_sales = df.groupby(['year', 'Month', 'Month_num']).agg({
        'Sales': 'sum'
    }).reset_index()
    monthly_sales = monthly_sales.sort_values(['year', 'Month_num'])
    
    fig = go.Figure()
    for year in monthly_sales['year'].unique():
        year_data = monthly_sales[monthly_sales['year'] == year]
        fig.add_trace(go.Scatter(
            x=year_data['Month'],
            y=year_data['Sales'],
            name=str(year),
            mode='lines+markers',
            line=dict(color=color_palette.get(year, '#000000'))
        ))
    
    fig.update_layout(
        title="Monthly Sales Trends by Year",
        xaxis_title="Month",
        yaxis_title="Sales ($)",
        xaxis=dict(categoryorder='array', categoryarray=MONTHS),
        height=400
    )
    
    return fig

def create_product_charts(df: pd.DataFrame):
    """Create product sales and profit charts."""
    col1, col2 = st.columns(2)
    
    with col1:
        create_top_products_chart(df, 'Sales', "Top 10 Selling Products")
    
    with col2:
        create_top_products_chart(df, 'Profit', "Top 10 Most Profitable Products")

def create_top_products_chart(df: pd.DataFrame, metric: str, title: str):
    """Create a bar chart for top products by metric."""
    top_products = (df.groupby('Product Name')[metric]
                   .sum()
                   .nlargest(10)
                   .reset_index())
    
    chart = alt.Chart(top_products).mark_bar(opacity=0.9, color="#9FC131").encode(
        x=alt.X(f'sum({metric}):Q'),
        y=alt.Y('Product Name:N', sort='-x')
    ).properties(title=title)
    
    st.altair_chart(chart, use_container_width=True)

def create_shipping_gauge(df: pd.DataFrame):
    """Create shipping days gauge chart."""
    value = int(np.round(df['days to ship'].mean()))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': "Average Shipping Days"},
        gauge={
            'axis': {'range': [df['days to ship'].min(), df['days to ship'].max()]},
            'bar': {'color': "#005C53"},
        }
    ))
    
    fig.update_layout(height=350)
    return fig

def create_sales_trend_chart(df: pd.DataFrame):
    """Create sales trend chart by category."""
    bars = alt.Chart(df).mark_bar().encode(
        y=alt.Y('sum(Sales):Q', stack='zero', axis=alt.Axis(format='~s')),
        x=alt.X('year:N'),
        color=alt.Color('Category:N', scale=alt.Scale(
            domain=list(CUSTOM_COLORS.keys()),
            range=list(CUSTOM_COLORS.values())
        ))
    )
    
    text = alt.Chart(df).mark_text(dx=-15, dy=30, color='white').encode(
        y=alt.Y('sum(Sales):Q', stack='zero'),
        x=alt.X('year:N'),
        detail='Category:N',
        text=alt.Text('sum(Sales):Q', format='~s')
    )
    
    return (bars + text).properties(
        title="Sales trends for Product Categories over the years"
    )

def main():
    """Main function to run the Streamlit dashboard."""
    st.set_page_config(**PAGE_CONFIG)
    set_page_style()
    
    # Load data
    df_original, grp_years_sales, grp_year_profit, grp_year_orders = load_data()
    
    # Create sidebar and filter data
    selected_year = create_sidebar(df_original)
    df = filter_data(df_original, selected_year)
    
    # Create dashboard sections
    create_header()
    
    create_kpi_metrics(
        df, grp_years_sales, grp_year_profit, grp_year_orders, selected_year
    )
    
    # Category Performance Analysis
    st.subheader("Category Performance Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_category_performance_chart(df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_order_distribution_chart(df), use_container_width=True)
    
    # Monthly sales trend
    st.subheader("Sales Trends")
    st.plotly_chart(create_monthly_sales_trend(df), use_container_width=True)
    
    # Product Performance
    st.subheader("Product Performance")
    create_product_charts(df)
    
    # Shipping and Category Trends
    st.subheader("Shipping and Category Trends")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(create_shipping_gauge(df), use_container_width=True)
    
    with col2:
        sales_trend_chart = create_sales_trend_chart(df)
        st.altair_chart(sales_trend_chart, use_container_width=True)

if __name__ == "__main__":
    main()