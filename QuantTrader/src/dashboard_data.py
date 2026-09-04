import math

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
from src import signals
from src import smc
from src.trade_history import save_trade
from src.risk import calculate_position_size


def _smart_round(value, price):
    """
    گرد کردن هوشمند بر اساس بزرگی خودِ قیمت - نه همیشه ۲ رقم اعشار ثابت.
    برای دارایی‌های ارزون (مثلاً یه توکن ۰.۰۶ دلاری) با ۲ رقم اعشار، Stop و
    TP1/TP2/TP3 همه به همون عدد گرد می‌شدن (چون تفاوت‌شون کوچیک‌تر از ۰.۰۱ بود)
    و عملاً بی‌فایده می‌شدن - این تابع رقم اعشار رو متناسب با قیمت انتخاب می‌کنه.
    """
    if value is None:
        return None
    abs_price = abs(price) if price else 0
    if abs_price >= 1:
        decimals = 2
    elif abs_price >= 0.01:
        decimals = 4
    elif abs_price >= 0.0001:
        decimals = 6
    else:
        decimals = 8
    return round(value, decimals)


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

            # ==========================
            # موتور ۱: اندیکاتورهای کلاسیک (EMA/RSI/MACD/حجم)
            # ==========================

            ema_score = signals.calculate_score(
                price, ema20, ema50, ema200, rsi14, macd_value, signal_value, volume, avg_volume,
            )
            ema_signal = signals.ema_signal_from_score(ema_score)
            ema_prob = signals.probability(ema_score)

            # ==========================
            # موتور ۲: Smart Money Concepts (Structure/BOS/CHOCH/OB/FVG)
            # ==========================

            smc_result = smc.build_smc_analysis(
                df["Open"].tolist(),
                df["High"].tolist(),
                df["Low"].tolist(),
                closes.tolist(),
                ema20, ema50, ema200,
            )
            smc_signal = signals.smc_signal_from_score(smc_result["score"])
            smc_prob = signals.smc_probability(smc_result["score"])

            # ==========================
            # ترکیب نهایی - طبق تصمیم مشترک با ربات تلگرام: سیگنال فقط وقتی
            # قوی/معتبره که هردو موتور موافق باشن، وگرنه محافظه‌کارانه HOLD.
            # همین چیزیه که مشکل قدیمی "۱۰۰٪ می‌شه بعد یهو برعکس" رو حل می‌کنه.
            # ==========================

            final_signal, combined_prob, engines_agree = signals.combine_signals(
                ema_signal, ema_prob, smc_signal, smc_prob,
            )

            signal = signals.signal_dict_to_string(final_signal)
            score = combined_prob - 50  # مقیاس رتبه‌بندی: مثبت=صعودی، منفی=نزولی
            prob = combined_prob

            entry = _smart_round(price, price)

            if "BUY" in signal.upper():

                stop = _smart_round(price * 0.985, price)
                tp1 = _smart_round(price * 1.015, price)
                tp2 = _smart_round(price * 1.03, price)
                tp3 = _smart_round(price * 1.05, price)

            elif "SELL" in signal.upper():

                stop = _smart_round(price * 1.015, price)
                tp1 = _smart_round(price * 0.985, price)
                tp2 = _smart_round(price * 0.97, price)
                tp3 = _smart_round(price * 0.95, price)

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
                _smart_round(price, price),
                signal,
                score,
                prob,
            )

            rows.append(
                {
                    "Coin": symbol,
                    "Price": _smart_round(price, price),
                    "SMA": _smart_round(sma20, price),
                    "EMA": _smart_round(ema20, price),
                    "EMA50": _smart_round(ema50, price),
                    "EMA200": _smart_round(ema200, price),
                    "RSI": round(rsi14, 2),
                    "Trend": trend(price, ema20),
                    "MACD": macd_signal_label(macd_value, signal_value),
                    "Score": score,
                    "Probability": f"{prob}%",
                    "Signal": signal,
                    "Agree": "✅" if engines_agree else "—",
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


def macd_signal_label(macd_line, signal_line):
    if macd_line > signal_line:
        return "🟢 Bullish"
    elif macd_line < signal_line:
        return "🔴 Bearish"
    return "🟡 Neutral"
