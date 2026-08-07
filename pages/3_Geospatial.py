import streamlit as st
import plotly.express as px
import urllib.request, json
import streamlit as st
from utils.data_loader import load_master

st.set_page_config(page_title="Geospatial — OlistIQ", page_icon="🗺️", layout="wide")
st.title("🗺️ Geospatial Analysis")
st.caption("Orders, revenue, and delivery times mapped across Brazilian states.")
st.divider()

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    with urllib.request.urlopen(url) as r:
        geo = json.loads(r.read())
    state_map = {
        "Acre":"AC","Alagoas":"AL","Amapá":"AP","Amazonas":"AM","Bahia":"BA",
        "Ceará":"CE","Distrito Federal":"DF","Espírito Santo":"ES","Goiás":"GO",
        "Maranhão":"MA","Mato Grosso":"MT","Mato Grosso do Sul":"MS",
        "Minas Gerais":"MG","Pará":"PA","Paraíba":"PB","Paraná":"PR",
        "Pernambuco":"PE","Piauí":"PI","Rio de Janeiro":"RJ",
        "Rio Grande do Norte":"RN","Rio Grande do Sul":"RS","Rondônia":"RO",
        "Roraima":"RR","Santa Catarina":"SC","São Paulo":"SP","Sergipe":"SE",
        "Tocantins":"TO"
    }
    for feat in geo["features"]:
        name = feat["properties"].get("name","")
        feat["id"] = state_map.get(name, name)
    return geo

_, df_d = load_master()
brazil_geo = load_geojson()

state_stats = df_d.groupby("customer_state").agg(
    orders=("order_id","nunique"),
    revenue=("revenue","sum"),
    avg_delivery=("delivery_days","mean"),
    late_rate=("is_late","mean")
).reset_index()
state_stats["late_rate"] = (state_stats["late_rate"] * 100).round(1)

col1, col2 = st.columns(2)

with col1:
    fig = px.choropleth(state_stats,
        geojson=brazil_geo, locations="customer_state",
        color="orders", hover_data=["revenue","avg_delivery"],
        title="Orders by State",
        color_continuous_scale="Blues", template="plotly_dark")
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.choropleth(state_stats,
        geojson=brazil_geo, locations="customer_state",
        color="avg_delivery", title="Avg Delivery Days by State",
        color_continuous_scale="RdYlGn_r", template="plotly_dark",
        hover_data=["orders","late_rate"])
    fig2.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig2, use_container_width=True)

# Late rate by state bar
fig3 = px.bar(state_stats.nlargest(10,"late_rate"),
              x="customer_state", y="late_rate",
              title="Top 10 States by Late Delivery Rate (%)",
              labels={"customer_state":"State","late_rate":"Late Rate (%)"},
              template="plotly_dark",
              color_discrete_sequence=["#ff4444"])
st.plotly_chart(fig3, use_container_width=True)
