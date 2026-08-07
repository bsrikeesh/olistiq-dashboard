import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st

DATA_DIR = Path("data")

@st.cache_data
def load_raw():
    orders    = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv", parse_dates=[
        "order_purchase_timestamp","order_approved_at",
        "order_delivered_carrier_date","order_delivered_customer_date",
        "order_estimated_delivery_date"
    ])
    items     = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
    products  = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")
    customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
    sellers   = pd.read_csv(DATA_DIR / "olist_sellers_dataset.csv")
    reviews   = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")
    payments  = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")
    cat_trans = pd.read_csv(DATA_DIR / "product_category_name_translation.csv")
    return orders, items, products, customers, sellers, reviews, payments, cat_trans

@st.cache_data
def load_master():
    orders, items, products, customers, sellers, reviews, payments, cat_trans = load_raw()

    products  = products.merge(cat_trans, on="product_category_name", how="left")
    pay_agg   = payments.groupby("order_id").agg(
        payment_value=("payment_value","sum"),
        payment_installments=("payment_installments","mean")
    ).reset_index()
    rev_agg   = reviews.groupby("order_id").agg(
        review_score=("review_score","mean")
    ).reset_index()

    df = (
        orders
        .merge(items,     on="order_id",    how="left")
        .merge(products,  on="product_id",  how="left")
        .merge(customers, on="customer_id", how="left")
        .merge(sellers,   on="seller_id",   how="left")
        .merge(pay_agg,   on="order_id",    how="left")
        .merge(rev_agg,   on="order_id",    how="left")
    )

    df["revenue"]       = df["price"] + df["freight_value"]
    df["order_month"]   = df["order_purchase_timestamp"].dt.to_period("M")
    df["order_year"]    = df["order_purchase_timestamp"].dt.year
    df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    df["is_late"]       = df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]
    df["category"]      = df["product_category_name_english"].fillna("Unknown")
    df_d                = df[df["order_status"] == "delivered"].copy()

    return df, df_d

@st.cache_data
def load_kpis():
    df, df_d = load_master()
    return {
        "total_revenue":     round(df_d["revenue"].sum(), 2),
        "total_orders":      df["order_id"].nunique(),
        "avg_order_value":   round(df_d.groupby("order_id")["revenue"].sum().mean(), 2),
        "unique_customers":  df["customer_unique_id"].nunique(),
        "avg_review":        round(df_d["review_score"].mean(), 2),
        "avg_delivery_days": round(df_d["delivery_days"].mean(), 1),
        "late_rate":         round(df_d["is_late"].mean() * 100, 1),
    }

@st.cache_data
def load_cohorts():
    _, df_d = load_master()
    df_c = df_d[["customer_unique_id","order_purchase_timestamp"]].dropna().copy()
    df_c["order_month"]  = df_c["order_purchase_timestamp"].dt.to_period("M")
    df_c["cohort_month"] = df_c.groupby("customer_unique_id")["order_month"].transform("min")
    df_c["period"]       = (df_c["order_month"] - df_c["cohort_month"]).apply(lambda x: x.n)
    cohort_data  = df_c.groupby(["cohort_month","period"])["customer_unique_id"].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index="cohort_month", columns="period", values="customer_unique_id")
    cohort_pct   = cohort_pivot.divide(cohort_pivot[0], axis=0) * 100
    return cohort_pct.iloc[:12, :7]
