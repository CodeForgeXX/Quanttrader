class SignalAI:

    def generate(self, market):

        score = 0

        # Trend
        if market.trend == "Bullish":
            score += 15
        elif market.trend == "Bearish":
            score -= 15

        # Structure
        if market.structure == "UPTREND":
            score += 20
        elif market.structure == "DOWNTREND":
            score -= 20

        # BOS
        if market.bos:
            if market.structure == "UPTREND":
                score += 20
            elif market.structure == "DOWNTREND":
                score -= 20

        # CHOCH
        if market.choch:
            if market.structure == "UPTREND":
                score += 10
            elif market.structure == "DOWNTREND":
                score -= 10

        # Liquidity
        if market.buy_side_liquidity:
            score += 10

        if market.sell_side_liquidity:
            score -= 10

        if market.liquidity_grab:
            score += 10

        # Order Block
        if market.bullish_ob:
            score += market.ob_strength // 5

        if market.bearish_ob:
            score -= market.ob_strength // 5

        # Fair Value Gap
        if market.bullish_fvg:
            score += 8

        if market.bearish_fvg:
            score -= 8

        # ذخیره امتیاز
        market.smart_money_score = score

        probability = min(95, max(5, abs(score)))
        market.probability = probability

        if probability >= 90:
            market.confidence = "VERY HIGH"
        elif probability >= 75:
            market.confidence = "HIGH"
        elif probability >= 60:
            market.confidence = "MEDIUM"
        else:
            market.confidence = "LOW"

        if score >= 35:
            market.signal = "BUY"

        elif score <= -35:
            market.signal = "SELL"

        else:
            market.signal = "WAIT"

        return market