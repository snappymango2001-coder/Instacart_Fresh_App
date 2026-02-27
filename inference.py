import pickle
import pandas as pd
import os
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

@st.cache_resource
def load_data():
    """Loads and caches the DataFrames once to keep the app fast."""
    # 1. Load Recommendation Table
    rec_path = os.path.join(ARTIFACTS_DIR, "recommendation_table.pkl")
    recommendation_table = pd.read_pickle(rec_path)
    
    # CRITICAL: Force user_id to integer to match Streamlit's number_input
    recommendation_table["user_id"] = recommendation_table["user_id"].astype(int)

    # 2. Load Products Metadata
    prod_path = os.path.join(ARTIFACTS_DIR, "products.pkl")
    products = pd.read_pickle(prod_path)
    
    # 3. Load Top Products (Cold Start)
    top_path = os.path.join(ARTIFACTS_DIR, "top_reordered_products.pkl")
    with open(top_path, "rb") as f:
        top_products = pickle.load(f)
        
    return recommendation_table, products, top_products

def recommend_products(user_id, top_n=10):
    recommendation_table, products, top_products = load_data()

    # Cast the input user_id to int just in case
    user_id = int(user_id)

    # Check if user exists in our trained model data
    if user_id not in recommendation_table["user_id"].values:
        # COLD START: Return trending products
        recs = products[products["product_id"].isin(top_products)]
        return recs[["product_id", "product_name"]].head(top_n), True

    # PERSONALIZED: Filter and sort by probability
    user_recs = recommendation_table[
        recommendation_table["user_id"] == user_id
    ].sort_values(by="prob", ascending=False)

    # Attach names from the products table
    user_recs = user_recs.merge(products, on="product_id")

    return user_recs[["product_id", "product_name", "prob"]].head(top_n), False