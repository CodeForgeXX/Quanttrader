class MultiTimeframeEngine:

    def analyze(self, analyses):

        bullish = 0
        bearish = 0

        for market in analyses:

            if market.trend == "Bullish":
                bullish += 1

            elif market.trend == "Bearish":
                bearish += 1

        if bullish >= 3:
            return "BULLISH"

        if bearish >= 3:
            return "BEARISH"

        return "NEUTRAL"