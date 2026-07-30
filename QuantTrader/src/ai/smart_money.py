from src.ai.trend_engine import TrendEngine


class SmartMoneyEngine:

    def __init__(self):

        self.trend_engine = TrendEngine()

    def analyze(self, market):

        trend = self.trend_engine.analyze(
            market.price,
            market.ema20,
            market.ema50,
            market.ema200,
        )

        score = trend["score"]

        if market.bos:
            score += 20

        if market.choch:
            score += 10

        if market.liquidity:
            score += 20

        if market.bullish_ob:
            score += 25

        if market.bullish_fvg:
            score += 25

        market.trend = trend["trend"]
        market.trend_score = trend["score"]

        market.smart_money_score = score

        if score >= 80:
            market.signal = "STRONG BUY"

        elif score >= 60:
            market.signal = "BUY"

        elif score <= -80:
            market.signal = "STRONG SELL"

        elif score <= -60:
            market.signal = "SELL"

        else:
            market.signal = "WAIT"

        return market