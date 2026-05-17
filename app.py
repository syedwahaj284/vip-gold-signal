import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# AUTO REFRESH
st_autorefresh(interval=30000, key="refresh")

# PAGE
st.set_page_config(
    page_title="VIP GOLD SIGNAL",
    layout="wide"
)

# SIDEBAR
st.sidebar.title("VIP SIGNAL PANEL")

pair = st.sidebar.selectbox(
    "SELECT PAIR",
    ["GC=F", "EURUSD=X", "GBPUSD=X", "BTC-USD"]
)

timeframe = st.sidebar.selectbox(
    "TIMEFRAME",
    ["5m", "15m", "1h"]
)

# TITLE
st.title("VIP LIVE TRADING DASHBOARD")

# DOWNLOAD DATA
data = yf.download(
    pair,
    period="5d",
    interval=timeframe,
    auto_adjust=True
)

# FIX COLUMNS
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

data.reset_index(inplace=True)

# EMA
data["EMA20"] = data["Close"].ewm(span=20).mean()
data["EMA50"] = data["Close"].ewm(span=50).mean()

# RSI
delta = data["Close"].diff()

gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

data["RSI"] = 100 - (100 / (1 + rs))

# LAST ROW
latest = data.iloc[-1]

price = float(latest["Close"])
ema20 = float(latest["EMA20"])
ema50 = float(latest["EMA50"])
rsi = float(latest["RSI"])

# SIGNAL
signal = "WAIT"
trend = "SIDEWAYS"

if price > ema20 and ema20 > ema50 and rsi > 55:
    signal = "BUY"
    trend = "BULLISH"

elif price < ema20 and ema20 < ema50 and rsi < 45:
    signal = "SELL"
    trend = "BEARISH"

# TP SL
tp = round(price + 10, 2)
sl = round(price - 5, 2)

if signal == "SELL":
    tp = round(price - 10, 2)
    sl = round(price + 5, 2)

# TOP CARDS
c1, c2, c3, c4 = st.columns(4)

c1.metric("PRICE", round(price, 2))
c2.metric("SIGNAL", signal)
c3.metric("TREND", trend)
c4.metric("RSI", round(rsi, 2))

# TP SL
d1, d2 = st.columns(2)

d1.success(f"TAKE PROFIT: {tp}")
d2.error(f"STOP LOSS: {sl}")

# CANDLE CHART
fig = go.Figure(data=[go.Candlestick(
    x=data["Datetime"],
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"]
)])

fig.add_trace(go.Scatter(
    x=data["Datetime"],
    y=data["EMA20"],
    line=dict(width=1),
    name="EMA20"
))

fig.add_trace(go.Scatter(
    x=data["Datetime"],
    y=data["EMA50"],
    line=dict(width=1),
    name="EMA50"
))

fig.update_layout(
    height=700
)

st.plotly_chart(fig, use_container_width=True)

# DATA
st.subheader("LIVE MARKET DATA")
st.dataframe(data.tail(10))
