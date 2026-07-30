class ProbabilityEngine:

    def calculate(self, market):

        # Only count factors that agree with the direction of the
        # signal that was actually generated (market.signal). Counting
        # bullish AND bearish factors together regardless of direction
        # made "probability" meaningless (a WAIT signal could score the
        # same as a BUY/SELL signal).

        if market.signal == "BUY":
            direction = 1
        elif market.signal == "SELL":
            direction = -1
        else:
            # No trade signal -> no directional probability
            market.probability = 0
            return market

        score = 0

        # Trend
        if market.trend == "Bullish":
            score += 20 if direction == 1 else 0
        elif market.trend == "Bearish":
            score += 20 if direction == -1 else 0

        # Structure
        if market.structure == "UPTREND":
            score += 15 if direction == 1 else 0
        elif market.structure == "DOWNTREND":
            score += 15 if direction == -1 else 0

        # BOS
        if market.bos:
            if (market.structure == "UPTREND" and direction == 1) or \
               (market.structure == "DOWNTREND" and direction == -1):
                score += 10

        # CHOCH
        if market.choch:
            if (market.structure == "UPTREND" and direction == 1) or \
               (market.structure == "DOWNTREND" and direction == -1):
                score += 10

        # Liquidity
        if market.liquidity_grab:
            score += 10

        # Order Block (only the block matching our direction counts)
        if market.bullish_ob and direction == 1:
            score += 10

        if market.bearish_ob and direction == -1:
            score += 10

        # Fair Value Gap (only the gap matching our direction counts)
        if market.bullish_fvg and direction == 1:
            score += 10

        if market.bearish_fvg and direction == -1:
            score += 10

        # EMA Alignment
        if market.ema20 > market.ema50 > market.ema200 and direction == 1:
            score += 5

        if market.ema20 < market.ema50 < market.ema200 and direction == -1:
            score += 5

        score = max(5, min(95, score))

        market.probability = score

        return market