class FVGEngine:

    def __init__(self):
        pass

    def analyze(self, df):

        highs = df["High"].tolist()
        lows = df["Low"].tolist()

        result = {
            "bullish_fvg": False,
            "bearish_fvg": False,
            "bullish_fvg_price": 0.0,
            "bearish_fvg_price": 0.0,
        }

        for i in range(2, len(df)):

            # Bullish FVG
            if lows[i] > highs[i - 2]:

                result["bullish_fvg"] = True
                result["bullish_fvg_price"] = (
                    lows[i] + highs[i - 2]
                ) / 2

            # Bearish FVG
            elif highs[i] < lows[i - 2]:

                result["bearish_fvg"] = True
                result["bearish_fvg_price"] = (
                    highs[i] + lows[i - 2]
                ) / 2

        return result