class CandleEngine:

    def analyze(self, df):

        last = df.iloc[-1]

        open_price = last["Open"]
        close_price = last["Close"]
        high = last["High"]
        low = last["Low"]

        body = abs(close_price - open_price)
        candle_range = high - low

        bullish = close_price > open_price
        bearish = close_price < open_price

        doji = False
        pinbar = False
        strong = False

        if candle_range > 0:

            body_ratio = body / candle_range

            if body_ratio < 0.20:
                doji = True

            if body_ratio > 0.70:
                strong = True

            upper_wick = high - max(open_price, close_price)
            lower_wick = min(open_price, close_price) - low

            if lower_wick > body * 2 or upper_wick > body * 2:
                pinbar = True

        return {
            "bullish": bullish,
            "bearish": bearish,
            "strong": strong,
            "doji": doji,
            "pinbar": pinbar,
        }