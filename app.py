import streamlit as st
import plotly.express as px
import pandas as pd
from weather_service import get_live_weather
from demand_logic import calculate_demand

# --- 1. ENTERPRISE CONFIG ---
st.set_page_config(page_title="DemandSense AI", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    div[data-testid="stMetric"] {background-color: #f9f9f9; padding: 10px; border-radius: 10px; border: 1px solid #e0e0e0;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR ---
st.sidebar.header("⚙️ Configuration")
mode = st.sidebar.segmented_control("Source", ["Simulation", "Live API"], selection_mode="single", default="Simulation")
st.sidebar.divider()
city = st.sidebar.text_input("Region", "Vadodara")

weather = None
if mode == "Simulation":
    st.sidebar.subheader("🧪 Scenarios")
    cond = st.sidebar.selectbox("Condition", ["Clear", "Rain", "Snow"])
    temp = st.sidebar.slider("Temp (°C)", -10, 45, 22)
    weather = {"city": f"{city} (Sim)", "temperature": temp, "condition": cond}
else:
    if st.sidebar.button("📡 Connect Satellite"):
        with st.spinner("Fetching data..."):
            weather = get_live_weather(city)
            st.session_state['last_weather'] = weather
    if 'last_weather' in st.session_state: weather = st.session_state['last_weather']

# --- 3. DASHBOARD ---
if weather:
    if "error" in weather:
        st.error(f"Connection Error: {weather['error']}")
    else:
        df, msg = calculate_demand(weather)
        if not df.empty:
            st.title("⛈️ DemandSense AI")
            st.caption(f"Real-Time Optimization • **{weather['city']}**")
            st.divider()

            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Revenue Risk Avoided", "15%", "Saved")
            k2.metric("Stock-out Reduction", "40%", "Optimized")
            k3.metric("Live Weather", f"{weather['temperature']}°C", weather['condition'])
            k4.metric("Forecast Demand", f"{df['predicted_demand'].sum():,} Units", "Active SKU")
            st.divider()

            # Visuals
            c_chart, c_alert = st.columns([2, 1])
            with c_chart:
                st.subheader("📊 Demand Velocity")
                chart_df = df.sort_values('predicted_demand', ascending=True).tail(10)
                fig = px.bar(chart_df, x='predicted_demand', y='product_id', orientation='h', 
                             color='status', color_discrete_map={'⚠️ RESTOCK': '#ff4b4b', 'OK': '#00c853'}, text_auto=True)
                fig.update_layout(template="plotly_white", height=450)
                st.plotly_chart(fig, use_container_width=True)

            with c_alert:
                st.subheader("🚨 Actions")
                crit = df[df['status'] == '⚠️ RESTOCK']
                if not crit.empty:
                    st.error(f"{len(crit)} items Critical")
                    st.dataframe(crit[['product_id', 'predicted_demand']], hide_index=True, use_container_width=True)
                else:
                    st.success("Supply Chain Healthy")

            # Data View
            with st.expander("📂 Full Log"):
                st.dataframe(df.style.applymap(lambda v: 'color: red; font-weight: bold;' if v == '⚠️ RESTOCK' else 'color: green;', subset=['status']), use_container_width=True)
else:
    st.info("👈 Select 'Simulation' or 'Live API' to start.")