import streamlit as st
import plotly.express as px
from utils.data_loader import load_master

st.set_page_config(page_title="Sellers — OlistIQ", page_icon="🏪", layout="wide")
st.title("🏪 Seller Performance")
st.caption("Top sellers by revenue, delivery time vs review score correlation.")
st.divider()

_, df_d = load_master()

seller_perf = df_d.groupby("seller_id").agg(
    revenue=("revenue","sum"),
    orders=("order_id","nunique"),
    avg_review=("review_score","mean"),
    avg_delivery=("delivery_days","mean"),
    late_rate=("is_late","mean")
).reset_index()
seller_perf["late_rate"] = (seller_perf["late_rate"] * 100).round(1)
seller_perf["seller_short"] = seller_perf["seller_id"].str[:8] + "..."

col1, col2, col3 = st.columns(3)
col1.metric("🏪 Total Sellers", f"{len(seller_perf):,}")
col2.metric("⭐ Avg Seller Rating", f"{seller_perf['avg_review'].mean():.2f}/5.0")
col3.metric("🚚 Avg Delivery Days", f"{seller_perf['avg_delivery'].mean():.1f}")

st.divider()

# Top 10 sellers by revenue
fig = px.bar(seller_perf.nlargest(10,"revenue"),
             x="seller_short", y="revenue",
             title="Top 10 Sellers by Revenue",
             color="avg_review", color_continuous_scale="RdYlGn",
             labels={"revenue":"Revenue (R$)","seller_short":"Seller","avg_review":"Avg Review"},
             template="plotly_dark")
fig.update_xaxes(tickangle=45)
st.plotly_chart(fig, use_container_width=True)

# Delivery vs review scatter
fig2 = px.scatter(seller_perf[seller_perf["orders"] >= 10],
                  x="avg_delivery", y="avg_review",
                  size="orders", color="late_rate",
                  title="Delivery Time vs Review Score (bubble = order count, color = late rate %)",
                  labels={
                      "avg_delivery":"Avg Delivery Days",
                      "avg_review":"Avg Review Score",
                      "late_rate":"Late Rate (%)"
                  },
                  template="plotly_dark",
                  color_continuous_scale="RdYlGn_r",
                  hover_data=["revenue"])
st.plotly_chart(fig2, use_container_width=True)

corr = seller_perf[["avg_delivery","avg_review"]].corr().iloc[0,1]
st.metric(
    "📊 Delivery vs Review Correlation",
    f"{corr:.3f}",
    help="Negative value = faster delivery → better reviews"
)

# Late delivery leaders
st.subheader("⚠️ Sellers with Highest Late Delivery Rate")
late_sellers = seller_perf[seller_perf["orders"] >= 5].nlargest(10,"late_rate")[["seller_short","orders","late_rate","avg_review","avg_delivery"]]
late_sellers.columns = ["Seller","Orders","Late Rate (%)","Avg Review","Avg Delivery (days)"]
st.dataframe(late_sellers.reset_index(drop=True), use_container_width=True)
