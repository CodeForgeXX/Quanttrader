class SwingDetector:

    def __init__(self, lookback=3):
        self.lookback = lookback

    def detect(self, df):

        highs = df["High"].tolist()
        lows = df["Low"].tolist()

        swing_highs = []
        swing_lows = []

        for i in range(self.lookback, len(df) - self.lookback):

            current_high = highs[i]
            current_low = lows[i]

            # Swing High
            if (
                current_high == max(highs[i - self.lookback : i + self.lookback + 1])
                and highs[i - self.lookback : i + self.lookback + 1].count(current_high) == 1
            ):
                swing_highs.append(i)

            # Swing Low
            if (
                current_low == min(lows[i - self.lookback : i + self.lookback + 1])
                and lows[i - self.lookback : i + self.lookback + 1].count(current_low) == 1
            ):
                swing_lows.append(i)

        return {
            "swing_highs": swing_highs,
            "swing_lows": swing_lows,
        }