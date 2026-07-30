class LiquidityEngine:

    def __init__(self, tolerance=0.001):
        self.tolerance = tolerance

    def analyze(self, df, swing_highs, swing_lows):

        highs = df["High"].tolist()
        lows = df["Low"].tolist()

        equal_highs = []
        equal_lows = []

        buy_side = False
        sell_side = False

        liquidity_grab = False

        # ---------- Equal Highs ----------

        for i in range(1, len(swing_highs)):

            current = highs[swing_highs[i]]
            previous = highs[swing_highs[i - 1]]

            if abs(current - previous) / previous <= self.tolerance:

                equal_highs.append(swing_highs[i])

        # ---------- Equal Lows ----------

        for i in range(1, len(swing_lows)):

            current = lows[swing_lows[i]]
            previous = lows[swing_lows[i - 1]]

            if abs(current - previous) / previous <= self.tolerance:

                equal_lows.append(swing_lows[i])

        # ---------- Buy Side Liquidity ----------

        if len(equal_highs) > 0:
            buy_side = True

        # ---------- Sell Side Liquidity ----------

        if len(equal_lows) > 0:
            sell_side = True

        # ---------- Liquidity Grab ----------

        if buy_side:

            last_high = max(highs)

            eq = highs[equal_highs[-1]]

            if last_high > eq:

                liquidity_grab = True

        if sell_side:

            last_low = min(lows)

            eq = lows[equal_lows[-1]]

            if last_low < eq:

                liquidity_grab = True

        return {

            "equal_highs": equal_highs,

            "equal_lows": equal_lows,

            "buy_side": buy_side,

            "sell_side": sell_side,

            "liquidity_grab": liquidity_grab,

        }