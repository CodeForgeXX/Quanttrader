class FVGEngine:

    def __init__(self):
        pass

    def analyze(
        self,
        highs,
        lows,
    ):

        if len(highs) < 3:

            return {
                "fvg": False
            }

        bullish_gap = lows.iloc[-1] > highs.iloc[-3]

        bearish_gap = highs.iloc[-1] < lows.iloc[-3]

        return {

            "fvg": bullish_gap or bearish_gap,

            "bullish": bullish_gap,

            "bearish": bearish_gap,

        }