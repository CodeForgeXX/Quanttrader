from src.signals import calculate_score, signal_from_score, probability


def trading_signal(
    price,
    ema20,
    ema50,
    ema200,
    rsi,
    macd_line,
    signal_line,
    volume,
    avg_volume,
):
    score = calculate_score(
        price,
        ema20,
        ema50,
        ema200,
        rsi,
        macd_line,
        signal_line,
        volume,
        avg_volume,
    )

    signal = signal_from_score(score)
    prob = probability(score)

    return score, signal, prob


def macd_signal(macd_line, signal_line):
    if macd_line > signal_line:
        return "🟢 Bullish"
    elif macd_line < signal_line:
        return "🔴 Bearish"
    return "🟡 Neutral"