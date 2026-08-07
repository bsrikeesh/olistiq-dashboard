import streamlit as st
from utils.data_loader import load_kpis

st.set_page_config(
    page_title="OlistIQ — E-Commerce Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("📦 OlistIQ")
st.sidebar.caption("Brazilian E-Commerce Intelligence")
st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset:** Olist (2016–2018)")
st.sidebar.markdown("**Orders:** 100K+")
st.sidebar.markdown("**Tables:** 9 joined")
st.sidebar.markdown("---")
st.sidebar.caption("Built by [B S Rikeesh](https://linkedin.com/in/bsrikeesh)")

st.title("📦 OlistIQ — E-Commerce Intelligence Dashboard")
st.markdown("**Multi-dimensional analytics on 100K+ Brazilian e-commerce orders across 9 relational tables.**")
st.divider()

with st.spinner("Loading data..."):
    kpis = load_kpis()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue",    f"R$ {kpis['total_revenue']:,.0f}")
col2.metric("📦 Total Orders",     f"{kpis['total_orders']:,}")
col3.metric("🛒 Avg Order Value",  f"R$ {kpis['avg_order_value']:,.2f}")
col4.metric("👥 Unique Customers", f"{kpis['unique_customers']:,}")

col5, col6, col7 = st.columns(3)
col5.metric("⭐ Avg Review Score",  f"{kpis['avg_review']}/5.0")
col6.metric("🚚 Avg Delivery Days", f"{kpis['avg_delivery_days']} days")
col7.metric("⚠️ Late Delivery Rate",f"{kpis['late_rate']}%")

st.divider()
st.markdown("### Navigate using the sidebar →")
st.markdown("""
| Page | What you'll find |
|------|-----------------|
| 📈 Overview | Revenue trends, monthly growth, order status breakdown |
| 🛍️ Products | Top categories, review scores, price distribution |
| 🗺️ Geospatial | Orders by state, delivery time heatmap across Brazil |
| 👥 Customers | Cohort retention matrix, CLV, repeat purchase rate |
| 🏪 Sellers | Top sellers by revenue, delivery vs rating correlation |
""")
