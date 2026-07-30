from src.ai.swing_detector import SwingDetector


class MarketStructure:

    def __init__(self):

        self.swing = SwingDetector()

    def analyze(self, df):

        swings = self.swing.detect(df)

        highs = swings["swing_highs"]
        lows = swings["swing_lows"]

        structure = "SIDEWAYS"

        bos = False
        choch = False

        if len(highs) >= 2:

            last_high = df["High"].iloc[highs[-1]]
            prev_high = df["High"].iloc[highs[-2]]

            if last_high > prev_high:
                structure = "UPTREND"
                bos = True

        if len(lows) >= 2:

            last_low = df["Low"].iloc[lows[-1]]
            prev_low = df["Low"].iloc[lows[-2]]

            if last_low < prev_low:
                structure = "DOWNTREND"
                bos = True

        if structure == "SIDEWAYS":
            choch = True

        return {
            "structure": structure,
            "bos": bos,
            "choch": choch,
            "swing_highs": highs,
            "swing_lows": lows,
        }