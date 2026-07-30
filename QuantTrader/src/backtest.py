from src.indicators import ema, rsi, macd
from src.strategy import trading_signal


def run_backtest(df):

    closes = df["Close"]

    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200)
    rsi14 = rsi(closes, 14)

    macd_line, signal_line, _ = macd(closes)

    trades = 0
    wins = 0
    losses = 0

    total_profit = 0

    for i in range(200, len(df) - 10):

        price = closes.iloc[i]

        volume = df["Volume"].iloc[i]
        avg_volume = df["Volume"].iloc[max(0, i - 20):i].mean()

        score, signal, prob = trading_signal(
            price,
            ema20.iloc[i],
            ema50.iloc[i],
            ema200.iloc[i],
            rsi14.iloc[i],
            macd_line.iloc[i],
            signal_line.iloc[i],
            volume,
            avg_volume,
        )

        if "BUY" not in signal.upper():
            continue

        trades += 1

        entry = price
        stop = entry * 0.985
        target = entry * 1.015

        result = None

        for j in range(i + 1, min(i + 10, len(df))):

            high = df["High"].iloc[j]
            low = df["Low"].iloc[j]

            if low <= stop:
                result = "LOSS"
                break

            if high >= target:
                result = "WIN"
                break

        if result == "WIN":
            wins += 1
            total_profit += (target - entry)

        elif result == "LOSS":
            losses += 1
            total_profit -= (entry - stop)

        else:
            # Neither stop-loss nor target was hit within the lookahead
            # window - the trade's outcome is undetermined, so it must
            # not be counted as a loss. Roll back the earlier increment
            # since we don't have a decided outcome for it.
            trades -= 1

    win_rate = 0

    if trades > 0:
        win_rate = round((wins / trades) * 100, 2)

    return {
        "Trades": trades,
        "Wins": wins,
        "Losses": losses,
        "WinRate": win_rate,
        "Profit": round(total_profit, 2),
    }