class BOSEngine:

    def __init__(self):
        pass

    def analyze(
        self,
        structure,
        highs,
        lows,
    ):

        if len(highs) < 3:
            return {
                "bos": False
            }

        last_high = highs.iloc[-1]
        prev_high = highs.iloc[-2]

        last_low = lows.iloc[-1]
        prev_low = lows.iloc[-2]

        bos = False

        if structure == "UPTREND":

            if last_high > prev_high:
                bos = True

        elif structure == "DOWNTREND":

            if last_low < prev_low:
                bos = True

        return {
            "bos": bos
        }