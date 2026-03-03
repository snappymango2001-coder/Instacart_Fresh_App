import random
import pickle
import pandas as pd
import plotly.express as px
import streamlit as st
from inference import recommend_products, load_data

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="InstaFresh - Shopping & Insights",
    page_icon="🥕",
    layout="wide"
)

st.session_state.setdefault("cart_count", 0)
st.session_state.setdefault("page", "search")
st.session_state.setdefault("active_user", None)


# ============================================================
# FRESH LIGHT ORANGE THEME & PLOTLY SETTINGS
# ============================================================
st.markdown("""
<style>
/* ===== MAIN BACKGROUND ===== */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #FFF5ED 0%, #FFEFD5 100%);
    color: #333333;
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #FFDAB9;
}

/* METRIC CARDS */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 20px;
    border: 1px solid #FF8200;
    box-shadow: 0 4px 15px rgba(255, 130, 0, 0.1);
}

/* PRODUCT BOXES */
.product-box {
    background: #FFFFFF;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #FFE4CC;
    transition: 0.3s ease;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.product-box:hover {
    transform: translateY(-4px);
    border: 1px solid #FF8200;
}

/* OVERRIDE TEXT COLORS FOR LIGHT THEME */
h1, h2, h3, h4, h5, h6, p, span, label {
    color: #4B2C20 !important; 
}

div.stButton > button:first-child {
    background: linear-gradient(90deg, #FF8200, #FFA500);
    color: white !important;
    border-radius: 12px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

px.defaults.template = "plotly_white" 
px.defaults.color_discrete_sequence = ["#FF8200", "#43B02A", "#FFA500", "#66BB6A"]

plot_layout = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#4B2C20"),
    margin=dict(l=20, r=20, t=50, b=20)
)

# ============================================================
# FORMATTERS
# ============================================================
def format_number(num):
    if num is None: return "0.00"
    abs_num = abs(num)
    if abs_num >= 1_000_000_000: return f"{num/1_000_000_000:.2f}B"
    elif abs_num >= 1_000_000: return f"{num/1_000_000:.2f}M"
    elif abs_num >= 1_000: return f"{num/1_000:.2f}K"
    else: return f"{num:.2f}"

def format_percent(num):
    return f"{num * 100:.2f}%"

# ============================================================
# DATA LOADER
# ============================================================
@st.cache_data
def get_dashboard_data():
    with open('artifacts/dashboard_stats.pkl', 'rb') as f:
        return pickle.load(f)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#43B02A;'>Insta<span style='color:#FF8200;'>Fresh</span></h1>", unsafe_allow_html=True)
    # This string must match the logic below exactly!
    app_mode = st.radio("Navigate", ["🛒 Grocery Recommender App", "📊 Data Insights"])
    st.divider()

    if app_mode == "🛒 Grocery Recommender App":
        st.write(f"**Basket:** {st.session_state.cart_count} Items")
        rec_table, _, _ = load_data()
        selected_user = st.selectbox(
            "Quick Select User ID",
            options=sorted(rec_table["user_id"].unique()))

# ============================================================
# 🛒 MODE: GROCERY RECOMMENDER APP (Modern UI Upgrade)
# ============================================================
if app_mode == "🛒 Grocery Recommender App":

    if st.session_state.page == "search":

        st.markdown("""
        <div style="text-align:center; padding:40px 20px 10px 20px;">
            <h1 style="font-size:42px; color:#43B02A; margin-bottom:10px;">
                🛒 What are we craving today?
            </h1>
            <p style="font-size:18px; color:#6B3E26; max-width:600px; margin:auto;">
                Discover fresh picks tailored just for you. 
                Choose your shopper ID below and unlock personalized grocery inspiration in seconds.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,2,1])

        with col2:
            st.image(
                "https://images.unsplash.com/photo-1542838132-92c53300491e?w=800",
                use_container_width=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            user_input = st.number_input(
                "Enter Your Customer ID",
                value=int(selected_user)
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("✨ Show My Fresh Picks"):
                st.session_state.active_user = user_input
                st.session_state.page = "results"
                st.rerun()

    # ---------------- RESULTS PAGE ----------------
    else:

        # Top Section
        top_col1, top_col2 = st.columns([3,1])

        with top_col1:
            st.markdown(f"""
            <h2 style="color:#43B02A; margin-bottom:0;">
                Fresh Picks for You
            </h2>
            <p style="color:#6B3E26; margin-top:5px;">
                Personalized recommendations based on your shopping habits.
            </p>
            """, unsafe_allow_html=True)

        with top_col2:
            st.markdown(f"""
            <div style="
                background:#FFF3E6;
                padding:15px;
                border-radius:15px;
                text-align:center;
                border:1px solid #FFD8B2;">
                <span style="color:#FF8200; font-weight:600;">
                    🧺 Basket
                </span><br>
                <span style="font-size:20px; font-weight:bold; color:#43B02A;">
                    {st.session_state.cart_count} items
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("← Back to Shop"):
            st.session_state.page = "search"
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        recs, is_new = recommend_products(st.session_state.active_user)

        if not recs.empty:
            for i in range(0, len(recs), 3):
                cols = st.columns(3)

                for j, (_, item) in enumerate(recs.iloc[i:i+3].iterrows()):
                    with cols[j]:
                        badge = "🌟 Personalized" if not is_new else "🔥 Trending"
                        price = round(random.uniform(1.99, 14.99), 2)

                        #Rendering the card visuals
                        st.markdown(f"""
                        <div class="product-box" style="margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="
                                    background:#FFF3E0;
                                    color:#FF8200;
                                    padding:6px 12px;
                                    border-radius:30px;
                                    font-size:12px;
                                    font-weight:600;">
                                    {badge}
                                </span>
                            </div>
                            <h3 style="margin:15px 0 5px 0; font-size: 1.1rem; min-height: 50px;">
                                {item["product_name"]}
                            </h3>
                            <h2 style="color:#43B02A; margin:0; padding-bottom:10px;">
                                ${price}
                            </h2>
                        </div>
                        """, unsafe_allow_html=True)

                        # We use use_container_width to make it fit the card perfectly
                        if st.button("➕ Add to Basket", key=f"add_{item['product_id']}", use_container_width=True):
                            st.session_state.cart_count += 1
                            st.toast(f"Added {item['product_name']} 🥕")
# ============================================================
# 📊 MODE: DATA INSIGHTS
# ============================================================
else:
    data = get_dashboard_data()
    lc = data['line_charts']
    avg_items_per_order = data['kpis']['total_product_lines'] / data['kpis']['total_orders']

    tab_exec, tab_prod, tab_cust = st.tabs(["📈 Executive", "📦 Products", "👥 Customers"])
# ================= EXECUTIVE =================
    with tab_exec:
        # 1. TOP LEVEL METRICS
        k1, k2, k3, k4 = st.columns(4)
        
        # Calculate key figures
        total_reorder_rate = lc['reorder_dow']['reordered'].mean()
        
        k1.metric("Total Orders", format_number(data['kpis']['total_orders']))
        k2.metric("Total Customers", format_number(data['kpis']['total_customers']))
        k3.metric("Avg Reorder Rate", format_percent(total_reorder_rate))
        k4.metric("Avg Items / Order", format_number(avg_items_per_order))

        st.divider()

        # 2. ROW 1: ORDER VOLUMES (Line Charts)
        st.subheader("Order Volume Trends")
        c1, c2 = st.columns(2)
        
        with c1:
            fig_ord_dow = px.line(lc['orders_dow'], 
                                 x='order_dow', y='order_count', 
                                 title="Total Orders by Day of Week",
                                 markers=True,
                                 color_discrete_sequence=["#43B02A"]) # Green for Volume
            fig_ord_dow.update_layout(**plot_layout)
            st.plotly_chart(fig_ord_dow, use_container_width=True)
        
        with c2:
            fig_ord_hr = px.line(lc['orders_hour'], 
                                x='order_hour_of_day', y='order_count', 
                                title="Total Orders by Hour of Day",
                                markers=True,
                                color_discrete_sequence=["#43B02A"]) # Green for Volume
            fig_ord_hr.update_layout(**plot_layout)
            st.plotly_chart(fig_ord_hr, use_container_width=True)

        # 3. ROW 2: REORDER RATES (Line Charts)
        st.subheader("Reorder Loyalty Trends")
        c3, c4 = st.columns(2)
        
        with c3:
            fig_re_dow = px.line(lc['reorder_dow'], 
                                x='order_dow', y='reordered', 
                                title="Reorder Rate by Day of Week",
                                markers=True, 
                                color_discrete_sequence=["#FF8200"]) # Orange for Loyalty
            fig_re_dow.update_layout(**plot_layout)
            st.plotly_chart(fig_re_dow, use_container_width=True)
            
        with c4:
            fig_re_hr = px.line(lc['reorder_hour'], 
                               x='order_hour_of_day', y='reordered', 
                               title="Reorder Rate by Hour of Day",
                               markers=True, 
                               color_discrete_sequence=["#FF8200"]) # Orange for Loyalty
            fig_re_hr.update_layout(**plot_layout)
            st.plotly_chart(fig_re_hr, use_container_width=True)

        # 4. ROW 3: PEAK TIMES (Heatmap)
        st.divider()
        st.subheader("🗓️ Peak Ordering Intensity")
        st.markdown("Concentration of order volume by day of week and hour of day.")
        
        fig_heat = px.imshow(
            data['heatmap'], 
            labels=dict(x="Hour of Day", y="Day of Week", color="Order Count"),
            y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            color_continuous_scale="Oranges",
            aspect="auto"
        )
        fig_heat.update_layout(**plot_layout)
        st.plotly_chart(fig_heat, use_container_width=True)

    # --- PRODUCTS TAB ---
    with tab_prod:
        pk1, pk2, pk3 = st.columns(3)
        pk1.metric("Unique Products", format_number(data['kpis']['total_products']))
        pk2.metric("Total Aisles", data['kpis']['total_aisles'])
        pk3.metric("Total Departments", data['kpis']['total_depts'])
        
        st.divider()
        st.subheader("🛒 Frequently Bought Together")
        st.dataframe(data['top_pairs'], use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Top 20 Reordered Products")
        top_20 = data['top_products'].sort_values('reordered', ascending=True).head(20)
        fig3 = px.bar(top_20, x='reordered', y='product_name', orientation='h', color_discrete_sequence=["#43B02A"])
        fig3.update_layout(**plot_layout)
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()
        st.subheader("Reordered vs. One-Time")
        fig_pie = px.pie(data['reorder_vs_one'], values='count', names='status', hole=0.5,
                         color_discrete_map={'Reordered': '#43B02A', 'One-Time Only': '#FF8200'})
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- CUSTOMERS TAB ---
    with tab_cust:
        st.subheader("User Segment Breakdown")
        col_pie1, col_pie2 = st.columns(2)
        with col_pie1:
            val_seg = data['user_segments']['value'].reset_index()
            val_seg.columns = ['Segment', 'Count']
            st.plotly_chart(px.pie(val_seg, values='Count', names='Segment', title="Value Segment", hole=0.4), use_container_width=True)
        with col_pie2:
            ord_seg = data['user_segments']['order'].reset_index()
            ord_seg.columns = ['Segment', 'Count']
            st.plotly_chart(px.pie(ord_seg, values='Count', names='Segment', title="Order Frequency", hole=0.4), use_container_width=True)

        st.divider()

# 3. Recency Distribution
        st.subheader("Purchase Recency")
        st.markdown("Distribution of days between orders for returning customers.")
        fig_rec = px.bar(data['recency_dist'], 
                 x='days_since_prior_order', 
                 y='count', 
                 title="Days Since Prior Order Distribution",
                 color_discrete_sequence=["#43B02A"]) 
        fig_rec.update_layout(**plot_layout)
        st.plotly_chart(fig_rec, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("<hr><center style='color:#9CA3AF;'>© 2026 InstaFresh Analytics</center>", unsafe_allow_html=True)
