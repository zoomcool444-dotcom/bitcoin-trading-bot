import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import random

# Page Setup
st.set_page_config(page_title="Pro Trading Platform", page_icon="📈", layout="wide")

# Custom Styling (Quotex / Dark Theme)
st.markdown("""
    <style>
    .main {background-color: #0e1117; color: white;}
    .stButton>button {width: 100%; border-radius: 5px; font-weight: bold; font-size: 18px;}
    .buy-btn {background-color: #28a745; color: white;}
    .sell-btn {background-color: #dc3545; color: white;}
    </style>
""", unsafe_allow_html=True)

# Top Bar / Balance Header
col_logo, col_demo, col_real, col_dep = st.columns([2, 1, 1, 1])
with col_logo:
    st.markdown("### ⚡ PRO-OPTION TRADING")
with col_demo:
    st.metric("Demo Balance", "$10,000.00")
with col_real:
    st.metric("Real Balance", "$0.00")
with col_dep:
    if st.button("💳 Deposit"):
        st.info("Binance Deposit page jald khulega!")

st.markdown("---")

# Main Workspace (Chart + Trading Panel)
chart_col, control_col = st.columns([3, 1])

with chart_col:
    st.subheader("📊 Live Market Chart (BTC/USD)")
    
    # Fetching Live Data
    @st.cache_data(ttl=30)
    def get_market_data():
        df = yf.download('BTC-USD', period='1d', interval='1m', progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df['SMA'] = df['Close'].rolling(window=5).mean()
        return df

    df = get_market_data()

    if not df.empty:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name='BTC'
        ))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1), name='SMA'))
        fig.update_layout(template='plotly_dark', height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with control_col:
    st.subheader("🎯 Trade Panel")
    amount = st.number_input("Investment ($)", min_value=1, max_value=1000, value=10)
    time_expiry = st.selectbox("Time", ["1 Min", "5 Min", "15 Min"])
    
    st.markdown("---")
    
    # TikTok Live Signal Box
    st.markdown("### 🤖 Bot Live Signal")
    latest_close = df['Close'].iloc[-1] if not df.empty else 0
    latest_sma = df['SMA'].iloc[-1] if not df.empty else 0
    
    if latest_close > latest_sma:
        st.success("🟢 SIGNAL: BUY / CALL")
    else:
        st.error("🔴 SIGNAL: SELL / PUT")
        
    st.markdown("---")
    
    if st.button("🟢 HIGHER (BUY)", key="buy"):
        st.success(f"Trade Placed: BUY ${amount} successfully!")
        
    if st.button("🔴 LOWER (SELL)", key="sell"):
        st.error(f"Trade Placed: SELL ${amount} successfully!")
