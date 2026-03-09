import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.abspath("."))

from src.data_cleaning import load_and_clean_data
from src.rfm_analysis import calculate_rfm
from src.clustering import perform_clustering


# ---------------- Page Config ---------------- #

st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    layout="wide",
)

# ---------------- Custom Style ---------------- #

st.markdown("""
<style>

[data-testid="stSidebar"]{
background-color:#111827;
}

[data-testid="stSidebar"] *{
color:white;
}

.metric-card{
background:#F9FAFB;
padding:20px;
border-radius:12px;
box-shadow:0 4px 10px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)


st.title("Customer Segmentation & Retention Dashboard")
st.write("Analyze customer behavior using **RFM analysis** and **K-Means clustering**.")


# ---------------- Load Data ---------------- #

@st.cache_data
def get_data():
    return load_and_clean_data("data/Online Retail Data Set.csv")

df = get_data()


# ---------------- Sidebar Filters ---------------- #

st.sidebar.title("Dashboard Filters")

selected_country = st.sidebar.multiselect(
    "Select Country",
    options=df["Country"].unique(),
    default=df["Country"].unique()
)

if len(selected_country) == 0:
    st.warning("Please select at least one country.")
    st.stop()

df = df[df["Country"].isin(selected_country)]


# ---------------- RFM Analysis ---------------- #

rfm = calculate_rfm(df)
rfm = perform_clustering(rfm)


# ---------------- Segment Names ---------------- #

segment_map = {
    0: "Regular Customers",
    1: "High Value Customers",
    2: "Occasional Customers",
    3: "At Risk Customers"
}

rfm["Segment"] = rfm["Cluster"].map(segment_map)


selected_segment = st.sidebar.multiselect(
    "Select Customer Segment",
    options=rfm["Segment"].unique(),
    default=rfm["Segment"].unique()
)

filtered_rfm = rfm[rfm["Segment"].isin(selected_segment)]


# ---------------- Key Metrics ---------------- #

st.subheader(" Key Business Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", filtered_rfm.shape[0])
col2.metric("Average Customer Spend", round(filtered_rfm["Monetary"].mean(), 2))
col3.metric("Total Revenue", round(filtered_rfm["Monetary"].sum(), 2))


# ---------------- Cluster Distribution ---------------- #

st.subheader("Customer Segment Distribution")

cluster_counts = filtered_rfm["Segment"].value_counts().reset_index()
cluster_counts.columns = ["Segment", "Customers"]

fig_bar = px.bar(
    cluster_counts,
    x="Segment",
    y="Customers",
    color="Segment",
    color_discrete_sequence=px.colors.qualitative.Set2,
    title="Customers per Segment"
)

st.plotly_chart(fig_bar, use_container_width=True)


# ---------------- Pie Charts ---------------- #

st.subheader("Segment Overview")

col1, col2 = st.columns(2)

# Segment share
fig_pie = px.pie(
    cluster_counts,
    names="Segment",
    values="Customers",
    title="Customer Segment Share",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

col1.plotly_chart(fig_pie, use_container_width=True)


# Revenue share
revenue_segment = filtered_rfm.groupby("Segment")["Monetary"].sum().reset_index()

fig_revenue_pie = px.pie(
    revenue_segment,
    names="Segment",
    values="Monetary",
    title="Revenue Contribution by Segment",
    color_discrete_sequence=px.colors.qualitative.Set3
)

col2.plotly_chart(fig_revenue_pie, use_container_width=True)


# ---------------- Customer Segmentation Scatter ---------------- #

st.subheader("Customer Segmentation (Frequency vs Spending)")

fig_scatter = px.scatter(
    filtered_rfm,
    x="Frequency",
    y="Monetary",
    color="Segment",
    color_discrete_sequence=px.colors.qualitative.Bold,
    title="Customer Segments"
)

st.plotly_chart(fig_scatter, use_container_width=True)


# ---------------- Top Customers ---------------- #

st.subheader("Top High Value Customers")

top_n = st.slider("Select number of top customers", 5, 50, 10)

top_customers = filtered_rfm.sort_values(
    by="Monetary", ascending=False
).head(top_n)

st.dataframe(top_customers)


# ---------------- Revenue by Country ---------------- #

st.subheader("Revenue by Country")

country_revenue = (
    df.groupby("Country")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig_country = px.bar(
    country_revenue,
    title="Top Countries by Revenue",
    color_discrete_sequence=["#6366F1"]
)

st.plotly_chart(fig_country, use_container_width=True)


# ---------------- Revenue Trend ---------------- #

st.subheader("Revenue Trend Over Time")

df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)

monthly_revenue = df.groupby("Month")["TotalPrice"].sum().reset_index()

fig_trend = px.line(
    monthly_revenue,
    x="Month",
    y="TotalPrice",
    markers=True,
    title="Monthly Revenue Trend"
)

st.plotly_chart(fig_trend, use_container_width=True)


# ---------------- Segment Insights ---------------- #

st.subheader("Customer Segment Insights")

segment_summary = filtered_rfm.groupby("Segment").agg({
    "Recency": "mean",
    "Frequency": "mean",
    "Monetary": "mean"
}).round(2)

st.dataframe(segment_summary)


# ---------------- Data Preview ---------------- #

st.subheader("Customer Data Preview")

st.dataframe(filtered_rfm.head(20))