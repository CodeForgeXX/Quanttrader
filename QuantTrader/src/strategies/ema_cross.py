from src.strategies.base_strategy import BaseStrategy


class EMACrossStrategy(BaseStrategy):
    """
    EMA Cross Strategy
    """

    def init(
        self,
        fast_column="EMA20",
        slow_column="EMA50",
    ):
        self.fast_column = fast_column
        self.slow_column = slow_column

    def analyze(self, data):

        if len(data) < 2:
            return "HOLD"

        previous = data.iloc[-2]
        current = data.iloc[-1]

        if (
            previous[self.fast_column]
            <= previous[self.slow_column]
            and
            current[self.fast_column]
            > current[self.slow_column]
        ):
            return "BUY"

        if (
            previous[self.fast_column]
            >= previous[self.slow_column]
            and
            current[self.fast_column]
            < current[self.slow_column]
        ):
            return "SELL"

        return "HOLD"