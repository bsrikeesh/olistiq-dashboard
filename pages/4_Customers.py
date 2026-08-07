import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.data_loader import load_master, load_cohorts

st.set_page_config(page_title="Customers — OlistIQ", page_icon="👥", layout="wide")
st.title("👥 Customer Behavior")
st.caption("Cohort retention, customer lifetime value, and repeat purchase patterns.")
st.divider()

_, df_d = load_master()
cohort_pct = load_cohorts()

# Cohort retention heatmap
fig = go.Figure(data=go.Heatmap(
    z=cohort_pct.values,
    x=[f"Month {i}" for i in cohort_pct.columns],
    y=[str(m) for m in cohort_pct.index],
    colorscale="Blues",
    text=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in cohort_pct.values],
    texttemplate="%{text}",
    showscale=True
))
fig.update_layout(
    title="Customer Cohort Retention Matrix (% returning per month)",
    xaxis_title="Months Since First Purchase",
    yaxis_title="Cohort Month",
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)
repeat_rate = (df_d.groupby("customer_unique_id")["order_id"].nunique() > 1).mean() * 100
clv = df_d.groupby("customer_unique_id")["revenue"].sum()
col1.metric("🔄 Repeat Purchase Rate", f"{repeat_rate:.1f}%")
col2.metric("💰 Avg CLV", f"R$ {clv.mean():,.2f}")
col3.metric("💎 Top 10% CLV Threshold", f"R$ {clv.quantile(0.9):,.2f}")

# CLV distribution
fig2 = px.histogram(clv, x="revenue", nbins=50,
                    title="Customer Lifetime Value Distribution",
                    labels={"revenue":"Total Revenue (R$)"},
                    template="plotly_dark",
                    color_discrete_sequence=["#00d4ff"])
fig2.update_layout(xaxis_range=[0, clv.quantile(0.95)])
st.plotly_chart(fig2, use_container_width=True)

# Days between purchases
orders_per_customer = df_d.sort_values("order_purchase_timestamp").groupby("customer_unique_id").agg(
    first_order=("order_purchase_timestamp","min"),
    last_order=("order_purchase_timestamp","max"),
    total_orders=("order_id","nunique")
).reset_index()
repeat_customers = orders_per_customer[orders_per_customer["total_orders"] > 1].copy()
repeat_customers["days_between"] = (repeat_customers["last_order"] - repeat_customers["first_order"]).dt.days

fig3 = px.histogram(repeat_customers, x="days_between", nbins=40,
                    title="Days Between First and Last Purchase (Repeat Customers Only)",
                    labels={"days_between":"Days"},
                    template="plotly_dark",
                    color_discrete_sequence=["#1A3F6F"])
st.plotly_chart(fig3, use_container_width=True)
