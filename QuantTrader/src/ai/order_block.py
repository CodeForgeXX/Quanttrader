class OrderBlockEngine:

    def __init__(self):
        pass

    def analyze(self, df, structure, swing_highs, swing_lows):

        highs = df["High"].tolist()
        lows = df["Low"].tolist()
        opens = df["Open"].tolist()
        closes = df["Close"].tolist()

        result = {
            "bullish_ob": False,
            "bearish_ob": False,
            "bullish_ob_price": 0.0,
            "bearish_ob_price": 0.0,
            "ob_strength": 0,
            "mitigated": False,
        }

        # -------- Bullish Order Block --------

        if structure == "UPTREND":

            for i in range(len(df) - 2, 1, -1):

                if closes[i] < opens[i]:

                    result["bullish_ob"] = True
                    result["bullish_ob_price"] = lows[i]

                    displacement = abs(closes[i + 1] - opens[i + 1])

                    result["ob_strength"] = min(
                        100,
                        int(displacement * 1000)
                    )

                    break

        # -------- Bearish Order Block --------

        elif structure == "DOWNTREND":

            for i in range(len(df) - 2, 1, -1):

                if closes[i] > opens[i]:

                    result["bearish_ob"] = True
                    result["bearish_ob_price"] = highs[i]

                    displacement = abs(opens[i + 1] - closes[i + 1])

                    result["ob_strength"] = min(
                        100,
                        int(displacement * 1000)
                    )

                    break

        # -------- Mitigation --------

        if result["bullish_ob"]:

            price = result["bullish_ob_price"]

            if lows[-1] <= price:

                result["mitigated"] = True

        if result["bearish_ob"]:

            price = result["bearish_ob_price"]

            if highs[-1] >= price:

                result["mitigated"] = True

        return result