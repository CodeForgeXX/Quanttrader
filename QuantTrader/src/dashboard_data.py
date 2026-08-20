import pandas as pd
import streamlit as st


from config.settings import (
    SYMBOLS,
    SMA_PERIOD,
    EMA_PERIOD,
    RSI_PERIOD,
    ACCOUNT_BALANCE,
    RISK_PERCENT,
)

from src.market import get_klines as _get_klines
from src.indicators import sma, ema, rsi, macd, trend
from src.strategy import trading_signal, macd_signal
from src.trade_history import save_trade
from src.risk import calculate_position_size


@st.cache_data(ttl=25, show_spinner=False)
def get_klines(symbol):
    """Cached wrapper around the raw fetch so repeated
    auto-refresh cycles (and the chart re-fetch for the selected coin)
    don't all hit the network separately within the same refresh
    window."""
    return _get_klines(symbol)


def get_dashboard_data():

    rows = []

    buy_count = 0
    sell_count = 0
    hold_count = 0

    for symbol in SYMBOLS:

        try:

            print(f"Processing {symbol}")

            df = get_klines(symbol)

            if df is None:
                continue

            closes = df["Close"]

            price = closes.iloc[-1]

            sma20 = sma(closes, SMA_PERIOD).iloc[-1]
            ema20 = ema(closes, EMA_PERIOD).iloc[-1]
            ema50 = ema(closes, 50).iloc[-1]
            ema200 = ema(closes, 200).iloc[-1]

            rsi14 = rsi(closes, RSI_PERIOD).iloc[-1]

            macd_line, signal_line, histogram = macd(closes)

            macd_value = macd_line.iloc[-1]
            signal_value = signal_line.iloc[-1]

            volume = df["Volume"].iloc[-1]
            avg_volume = df["Volume"].tail(20).mean()

            score, signal, prob = trading_signal(
                price,
                ema20,
                ema50,
                ema200,
                rsi14,
                macd_value,
                signal_value,
                volume,
                avg_volume,
            )

            entry = round(price, 2)

            if "BUY" in signal.upper():

                stop = round(price * 0.985, 2)
                tp1 = round(price * 1.015, 2)
                tp2 = round(price * 1.03, 2)
                tp3 = round(price * 1.05, 2)

            elif "SELL" in signal.upper():

                stop = round(price * 1.015, 2)
                tp1 = round(price * 0.985, 2)
                tp2 = round(price * 0.97, 2)
                tp3 = round(price * 0.95, 2)

            else:

                stop = None
                tp1 = None
                tp2 = None
                tp3 = None

            risk_reward = None

            if stop is not None and tp1 is not None:

                try:

                    risk = abs(entry - stop)
                    reward = abs(tp1 - entry)

                    if risk != 0:
                        risk_reward = round(reward / risk, 2)

                except Exception:
                    risk_reward = None

            # ==========================
            # Risk Management
            # ==========================

            if stop is not None:

                risk_info = calculate_position_size(
    balance=ACCOUNT_BALANCE,
    risk_percent=RISK_PERCENT,
    entry=entry,
    stop=stop,
)

                position_size = risk_info["position_size"]
                risk_amount = risk_info["risk_amount"]

            else:

                position_size = None
                risk_amount = None

            # ==========================

            if "BUY" in signal.upper():
                buy_count += 1

            elif "SELL" in signal.upper():
                sell_count += 1

            else:
                hold_count += 1

            save_trade(
                symbol,
                round(price, 2),
                signal,
                score,
                prob,
            )

            rows.append(
                {
                    "Coin": symbol,
                    "Price": round(price, 2),
                    "SMA": round(sma20, 2),
                    "EMA": round(ema20, 2),
                    "EMA50": round(ema50, 2),
                    "EMA200": round(ema200, 2),
                    "RSI": round(rsi14, 2),
                    "Trend": trend(price, ema20),
                    "MACD": macd_signal(macd_value, signal_value),
                    "Score": score,
                    "Probability": f"{prob}%",
                    "Signal": signal,
                    "Entry": entry,
                    "Stop": stop,
                    "TP1": tp1,
                    "TP2": tp2,
                    "TP3": tp3,
                    "RR": risk_reward,
                    "Position Size": position_size,
                    "Risk $": risk_amount,
                }
            )

        except Exception as e:
            print(f"ERROR in {symbol}: {e}")

    table = pd.DataFrame(rows)

    stats = {
        "coins": len(table),
        "buy": buy_count,
        "sell": sell_count,
        "hold": hold_count,
    }

    return table, stats
