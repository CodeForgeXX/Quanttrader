from enum import Enum


class Trend(Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    SIDEWAYS = "Sideways"


class TrendEngine:

    def __init__(self):
        self.trend = Trend.SIDEWAYS

    def analyze(
        self,
        price,
        ema20,
        ema50,
        ema200,
    ):

        score = 0

        if price > ema20:
            score += 20
        else:
            score -= 20

        if ema20 > ema50:
            score += 30
        else:
            score -= 30

        if ema50 > ema200:
            score += 50
        else:
            score -= 50

        if score >= 50:
            self.trend = Trend.BULLISH

        elif score <= -50:
            self.trend = Trend.BEARISH

        else:
            self.trend = Trend.SIDEWAYS

        return {
            "trend": self.trend.value,
            "score": score,
        }