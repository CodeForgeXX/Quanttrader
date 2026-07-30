def calculate_score(price, ema20, ema50, ema200, rsi, macd_line, signal_line, volume, avg_volume):
    score = 0

    # EMA
    if price > ema20:
        score += 1
    if price > ema50:
        score += 2
    if price > ema200:
        score += 3

    # RSI
    if rsi < 30:
        score += 3
    elif rsi < 45:
        score += 1
    elif rsi > 70:
        score -= 3
    elif rsi > 55:
        score -= 1

    # MACD
    if macd_line > signal_line:
        score += 3
    else:
        score -= 3

    # Volume
    if volume > avg_volume:
        score += 2

    return score


def signal_from_score(score):
    if score >= 10:
        return "🟢 STRONG BUY"
    elif score >= 6:
        return "🟢 BUY"
    elif score >= 3:
        return "🟡 HOLD"
    elif score >= 0:
        return "🟠 WEAK SELL"
    else:
        return "🔴 STRONG SELL"


def probability(score):
    value = max(0, min(100, 50 + score * 5))
    return value