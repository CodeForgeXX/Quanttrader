from src.market import get_klines


class MarketData:

    def __init__(self):
        pass

    def get_market_data(self, symbol):

        df = get_klines(symbol)

        if df is None:
            return None

        return df