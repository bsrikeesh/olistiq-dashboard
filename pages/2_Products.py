import streamlit as st
import plotly.express as px
from utils.data_loader import load_master

st.set_page_config(page_title="Products — OlistIQ", page_icon="🛍️", layout="wide")
st.title("🛍️ Product Analytics")
st.caption("Category revenue, review scores, and price distribution.")
st.divider()

_, df_d = load_master()

col1, col2 = st.columns(2)

with col1:
    cat_rev = df_d.groupby("category")["revenue"].sum().nlargest(10).reset_index()
    fig = px.bar(cat_rev, x="revenue", y="category", orientation="h",
                 title="Top 10 Categories by Revenue",
                 labels={"revenue":"Revenue (R$)","category":"Category"},
                 template="plotly_dark", color="revenue",
                 color_continuous_scale="Blues")
    fig.update_layout(yaxis={"categoryorder":"total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    cat_review = df_d.groupby("category").agg(
        revenue=("revenue","sum"),
        review=("review_score","mean"),
        orders=("order_id","nunique")
    ).nlargest(15,"revenue").reset_index()
    fig2 = px.scatter(cat_review, x="revenue", y="review",
                      size="orders", hover_name="category",
                      title="Revenue vs Review Score (bubble = order count)",
                      labels={"revenue":"Revenue (R$)","review":"Avg Review Score"},
                      template="plotly_dark", color="review",
                      color_continuous_scale="RdYlGn")
    st.plotly_chart(fig2, use_container_width=True)

# Price distribution
top5 = cat_rev["category"].head(5).tolist()
fig3 = px.box(df_d[df_d["category"].isin(top5)],
              x="category", y="price",
              title="Price Distribution — Top 5 Categories",
              template="plotly_dark", color="category")
st.plotly_chart(fig3, use_container_width=True)

# Review score distribution
fig4 = px.histogram(df_d.dropna(subset=["review_score"]),
                    x="review_score", nbins=5,
                    title="Overall Review Score Distribution",
                    labels={"review_score":"Review Score"},
                    template="plotly_dark",
                    color_discrete_sequence=["#00d4ff"])
st.plotly_chart(fig4, use_container_width=True)
