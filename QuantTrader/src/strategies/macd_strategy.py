from src.strategies.base_strategy import BaseStrategy


class MACDStrategy(BaseStrategy):
    """
    MACD Crossover Strategy
    """

    def init(
        self,
        macd_column="MACD",
        signal_column="MACD_SIGNAL",
    ):
        self.macd_column = macd_column
        self.signal_column = signal_column

    def analyze(self, data):

        if len(data) < 2:
            return "HOLD"

        previous = data.iloc[-2]
        current = data.iloc[-1]

        if (
            previous[self.macd_column]
            <= previous[self.signal_column]
            and
            current[self.macd_column]
            > current[self.signal_column]
        ):
            return "BUY"

        if (
            previous[self.macd_column]
            >= previous[self.signal_column]
            and
            current[self.macd_column]
            < current[self.signal_column]
        ):
            return "SELL"

        return "HOLD"