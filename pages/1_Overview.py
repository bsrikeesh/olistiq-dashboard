import streamlit as st
import plotly.express as px
from utils.data_loader import load_master

st.set_page_config(page_title="Overview — OlistIQ", page_icon="📈", layout="wide")
st.title("📈 Executive Overview")
st.caption("Revenue trends, order volume, and status breakdown.")
st.divider()

df, df_d = load_master()

# Monthly revenue trend
monthly = df_d.groupby("order_month")["revenue"].sum().reset_index()
monthly["order_month"] = monthly["order_month"].astype(str)
fig = px.line(monthly, x="order_month", y="revenue",
              title="Monthly Revenue Trend",
              labels={"order_month":"Month","revenue":"Revenue (R$)"},
              template="plotly_dark")
fig.update_traces(line_color="#00d4ff", line_width=2.5)
fig.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

# Order status
with col1:
    status = df["order_status"].value_counts().reset_index()
    fig2 = px.pie(status, names="order_status", values="count",
                  title="Order Status Distribution",
                  template="plotly_dark", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# Monthly order volume
with col2:
    monthly_orders = df.groupby("order_month")["order_id"].nunique().reset_index()
    monthly_orders["order_month"] = monthly_orders["order_month"].astype(str)
    fig3 = px.bar(monthly_orders, x="order_month", y="order_id",
                  title="Monthly Order Volume",
                  labels={"order_month":"Month","order_id":"Orders"},
                  template="plotly_dark",
                  color_discrete_sequence=["#1A3F6F"])
    fig3.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig3, use_container_width=True)

# YoY revenue
st.subheader("Year-on-Year Revenue")
yoy = df_d.groupby("order_year")["revenue"].sum().reset_index()
fig4 = px.bar(yoy, x="order_year", y="revenue",
              title="Revenue by Year",
              labels={"order_year":"Year","revenue":"Revenue (R$)"},
              template="plotly_dark",
              color_discrete_sequence=["#00d4ff"])
st.plotly_chart(fig4, use_container_width=True)
