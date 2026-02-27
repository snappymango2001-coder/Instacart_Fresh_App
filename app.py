import streamlit as st
import time
import random
from inference import recommend_products, load_data

# -------------------- Session State Logic --------------------
if "cart_count" not in st.session_state:
    st.session_state.cart_count = 0
if "page" not in st.session_state:
    st.session_state.page = "search"

# --- Page Config ---
st.set_page_config(page_title="Instacart Fresh", page_icon="🥕", layout="wide")

# --- Modern UI Styling (Orange & Green Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #2D2D2D !important; font-family: 'Inter', sans-serif; }
    
    .product-box {
        background-color: white;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #F0F0F0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        text-align: center;
        transition: 0.3s;
    }
    .product-box:hover { border: 1px solid #FF8200; transform: translateY(-3px); }

    .badge {
        background-color: #FFF3E0;
        color: #FF8200;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }

    div.stButton > button:first-child {
        background-color: #43B02A;
        color: white;
        border-radius: 12px;
        border: none;
        height: 3em;
        width: 100%;
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] {
        background-color: #F7F7F7;
        border-right: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <h1 style="margin:0; color:#43B02A !important;">Insta<span style="color:#FF8200;">Fresh</span></h1>
            <p style="font-size:12px; color:#888;">SUPERFAST GROCERIES</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Cart Status (Non-button)
    st.markdown(f"""
        <div style="padding: 10px; text-align: center;">
            <span style="font-size: 24px;">🛒</span><br>
            <b style="color: #43B02A;">{st.session_state.cart_count} Items</b> in your basket
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Data Loading (Core logic)
    rec_table, _, _ = load_data()
    all_users = sorted(rec_table["user_id"].unique())
    
    st.subheader("👤 User Profile")
    selected_user = st.selectbox("Quick Select ID", options=all_users)
    
    if st.session_state.page == "results":
        if st.button("← Back to Shop"):
            st.session_state.page = "search"
            st.rerun()

# --- Main Logic Flow ---

if st.session_state.page == "search":
    # -------------------- PAGE 1: SEARCH --------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=800&q=80", use_container_width=True)
        st.markdown("<h2 style='text-align: center;'>What are we craving today?.</h2>", unsafe_allow_html=True)
        
        user_input = st.number_input("Enter your Customer ID", value=int(selected_user), step=1)
        
        if st.button("Unlock Personalized Aisle ✨"):
            with st.status("📦 Loading freshness please wait!......", expanded=True) as status:
                time.sleep(1.5) 
                st.session_state.active_user = user_input
                st.session_state.page = "results"
                status.update(label="Welcome to your store!", state="complete", expanded=False)
                st.rerun()

else:
    # -------------------- PAGE 2: RESULTS --------------------
    st.markdown(f"### ✨ Fresh Picks for User #{st.session_state.active_user}")
    
    # Core ML Function Call
    recs, is_new = recommend_products(st.session_state.active_user)
    
    if not recs.empty:
        rows = [recs.iloc[i:i+3] for i in range(0, len(recs), 3)]
        
        for row_data in rows:
            cols = st.columns(3)
            for i, (_, item) in enumerate(row_data.iterrows()):
                with cols[i]:
                    badge_text = "Personalized" if not is_new else "Trending"
                    
                    # RANDOM PRICE GENERATION
                    # We use product_id as a seed so the price doesn't change every time you click 'Add to Cart'
                    random.seed(int(item['product_id']))
                    price = round(random.uniform(1.99, 14.99), 2)
                    
                    st.markdown(f"""
                        <div class="product-box">
                            <span class="badge">{badge_text}</span>
                            <div style="font-size: 60px; margin: 15px 0;">📦</div>
                            <h3 style="font-size: 18px; margin: 0;">{item['product_name']}</h3>
                            <p style="color: #888; font-size: 11px;">Product ID: {item['product_id']}</p>
                            <h2 style="color: #43B02A; margin: 10px 0;">${price}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Add to Basket", key=f"add_{item['product_id']}"):
                        st.session_state.cart_count += 1
                        st.toast(f"✅ {item['product_name']} added!", icon="🍊")
                        time.sleep(0.4)
                        st.rerun()
    else:
        st.error("No products found for this ID.")
        if st.button("Try another ID"):
            st.session_state.page = "search"
            st.rerun()

st.markdown("<br><hr><center style='color: #ccc;'>© 2026 InstaFresh • Secure Checkout Enabled</center>", unsafe_allow_html=True)