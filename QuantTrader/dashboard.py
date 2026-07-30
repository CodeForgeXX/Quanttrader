from streamlit_autorefresh import st_autorefresh
from src.backtest import run_backtest
import os
import pandas as pd
import streamlit as st
def load_css():
    with open("assets/styles.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )

load_css()

from config.settings import VERSION
from src.dashboard_data import get_dashboard_data, get_klines
from src.charts import create_candlestick

st.set_page_config(
    page_title="QuantTrader",
    page_icon="📈",
    layout="wide",
)
st_autorefresh(
    interval=30000,
    key="quanttrader_refresh_001",
)
st.markdown(
    """
    <h1 style='margin-bottom:0px;'>
        🚀 QuantTrader PRO X
    </h1>

    <p style='color:#9ca3af;
              font-size:18px;
              margin-top:0px;'>
        Live Crypto Intelligence
    </p>
    """,
    unsafe_allow_html=True,
)

table, stats = get_dashboard_data()
# ==========================
# Best Trade
# ==========================

if not table.empty:

    best_trade = table.sort_values(
        by="Score",
        ascending=False,
    ).iloc[0]

    st.success(
        f"""
🔥 BEST TRADE NOW

🪙 {best_trade['Coin']}

📢 {best_trade['Signal']}

🎯 Probability : {best_trade['Probability']}

⭐ Score : {best_trade['Score']}

💰 Entry : {best_trade['Entry']}

🛑 Stop : {best_trade['Stop']}

🎯 TP1 : {best_trade['TP1']}
"""
    )

st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Coins", stats["coins"])
col2.metric("BUY", stats["buy"])
col3.metric("SELL", stats["sell"])
col4.metric("HOLD", stats["hold"])

st.divider()

if table.empty:
    st.error("❌ No market data received from Binance.")
    st.stop()

st.subheader("📊 Market Overview")

st.dataframe(
    table,
    width="stretch",
    hide_index=True,
)

if table.empty:
    st.error("No market data received.")
    st.stop()

selected = st.selectbox(
    "🪙 Select Coin",
    table["Coin"].tolist(),
)

df = get_klines(selected)

if df is None:
    st.error(f"Cannot load {selected}")
    st.stop()

st.subheader(f"📈 {selected} Live Chart")

fig = create_candlestick(
    df,
    selected,
)

st.plotly_chart(
    fig,
    width="stretch",
)

latest = df.iloc[-1]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Open", f"{latest['Open']:.2f}")
c2.metric("High", f"{latest['High']:.2f}")
c3.metric("Low", f"{latest['Low']:.2f}")
c4.metric("Close", f"{latest['Close']:.2f}")

st.divider()

st.subheader("📜 Trade History")
st.divider()
st.divider()

st.subheader("📈 Backtest")

if st.button("▶ Run Backtest"):

    result = run_backtest(df)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Trades", result["Trades"])
    c2.metric("Wins", result["Wins"])
    c3.metric("Losses", result["Losses"])
    c4.metric("Win Rate", f"{result['WinRate']}%")

    st.success(f"Net Profit : {result['Profit']}")

if os.path.exists("data/trades.csv"):
    history = pd.read_csv("data/trades.csv")
    st.dataframe(
        history.tail(20),
        width="stretch",
        hide_index=True,
    )
else:
    st.info("No trades recorded.")
