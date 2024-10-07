# 📈 Insightify Dashboard

A powerful and interactive sales analytics dashboard built with Streamlit, offering comprehensive insights into superstore sales data.

## 🌟 Features

- **Real-time KPI Metrics**: Track sales, profit, and order volumes with year-over-year changes
- **Interactive Filtering**: Filter data by year for targeted analysis
- **Rich Visualizations**:
  - Category Performance Scatter Plot
  - Order Distribution Sunburst Chart
  - Monthly Sales Trends Line Chart
  - Top Products Analysis
  - Shipping Performance Gauge
  - Category Sales Trends

## 🛠️ Tech Stack

- **Streamlit**: Core framework for building the web application
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive plotting (scatter plots, sunburst charts, gauges)
- **Altair**: Declarative statistical visualizations
- **NumPy**: Numerical computations
- **Millify**: Number formatting

## 📋 Prerequisites

- Python 3.12+
- Required Python packages:
  ```
  streamlit
  pandas
  numpy
  plotly
  altair
  millify
  ```
- Excel dataset: `superstore_enriched.xlsx`

## 🚀 Installation & Running

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

## 📊 Dashboard Sections

### 1. KPI Metrics
- Sales total with YoY change
- Profit total with YoY change
- Order count with YoY change

### 2. Category Performance Analysis
- Scatter plot showing Sales vs Profit by Category
- Sunburst chart displaying order distribution by Region and Segment

### 3. Sales Trends
- Interactive line chart showing monthly sales trends by year

### 4. Product Performance
- Top 10 selling products
- Top 10 most profitable products

### 5. Shipping and Category Trends
- Gauge chart showing average shipping days
- Stacked bar chart displaying sales trends by product category

## 🎨 Customization

The dashboard uses a custom color palette:
```python
CUSTOM_COLORS = {
    'Furniture': '#005C53',
    'Office Supplies': '#9FC131',
    'Technology': '#042940'
}
```

## 🔧 Performance Optimizations

- Data loading is cached using `@st.cache_data`
- Efficient data filtering and aggregation
- Responsive layout using Streamlit's column system

## 📝 Code Structure

- **Constants**: Configuration and color definitions
- **Data Loading**: Cached data loading and preprocessing
- **UI Styling**: Custom styling for metrics and layout
- **Dashboard Components**: Modular functions for each visualization
- **Main Function**: Orchestrates the dashboard assembly

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.