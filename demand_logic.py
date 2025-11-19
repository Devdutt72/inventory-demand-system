import pandas as pd
import psycopg2
import streamlit as st

# 🔒 SECURE: Fetch from secrets
DB_URI = st.secrets["DB_URI"]

@st.cache_data(ttl=600)
def load_inventory():
    try:
        conn = psycopg2.connect(DB_URI)
        df = pd.read_sql("SELECT * FROM inventory", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def calculate_demand(weather):
    df = load_inventory().copy()
    if df.empty: return df, "❌ DB Connection Failed"

    temp = weather.get('temperature', 25)
    cond = weather.get('condition', 'Clear')
    is_raining = 'Rain' in cond or 'Drizzle' in cond
    
    df['multiplier'] = 1.0
    msg = "✅ Market Stable"

    # --- LOGIC ENGINE ---
    
    # 1. Rain Logic
    if is_raining:
        df.loc[df['category'] == 'Monsoon', 'multiplier'] = 3.5
        df.loc[df['category'] == 'Summer', 'multiplier'] = 0.2
        msg = "🌧️ Rain Alert: Monsoon Spike"

    # 2. Temperature Overrides (Fixes Winter/Summer bugs)
    if temp < 20: 
        df.loc[df['category'] == 'Summer', 'multiplier'] = 0.05 
        df.loc[df['category'] == 'Winter', 'multiplier'] = 2.5
        if not is_raining: msg = f"❄️ Low Temp ({temp}°C): Winter Surge"

    elif temp > 32:
        df.loc[df['category'] == 'Winter', 'multiplier'] = 0.05
        df.loc[df['category'] == 'Summer', 'multiplier'] = 2.0
        if not is_raining: msg = f"☀️ High Heat ({temp}°C): Summer Surge"

    # 3. Calculate
    df['predicted_demand'] = (df['base_demand'] * df['multiplier']).astype(int)
    df['status'] = 'OK'
    df.loc[df['predicted_demand'] > df['current_stock'], 'status'] = '⚠️ RESTOCK'
    
    return df, msg