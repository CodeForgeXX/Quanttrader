from src.strategies.base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    RSI Strategy
    """

    def init(
        self,
        rsi_column="RSI",
        overbought=70,
        oversold=30,
    ):
        self.rsi_column = rsi_column
        self.overbought = overbought
        self.oversold = oversold

    def analyze(self, data):

        if len(data) == 0:
            return "HOLD"

        rsi = data.iloc[-1][self.rsi_column]

        if rsi <= self.oversold:
            return "BUY"

        if rsi >= self.overbought:
            return "SELL"

        return "HOLD"