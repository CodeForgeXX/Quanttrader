import pandas as pd


def sma(prices, period=20):
    return prices.rolling(window=period).mean()


def ema(prices, period=20):
    return prices.ewm(span=period, adjust=False).mean()


def rsi(prices, period=14):

    delta = prices.diff()

    gain = delta.where(delta > 0, 0)

    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def macd(prices):

    ema12 = prices.ewm(span=12, adjust=False).mean()

    ema26 = prices.ewm(span=26, adjust=False).mean()

    macd_line = ema12 - ema26

    signal_line = macd_line.ewm(span=9, adjust=False).mean()

    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def trend(price, ema_value):

    if price > ema_value:
        return "🟢 Bullish"

    elif price < ema_value:
        return "🔴 Bearish"

    return "🟡 Sideways"