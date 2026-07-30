from config.settings import DEFAULT_INTERVAL

from src.services.market_service import MarketService

from src.core.signal_generator import SignalGenerator


class TradingEngine:

    def __init__(self):

        self.market = MarketService()

        self.signal_generator = SignalGenerator()

    def analyze(self, symbol):

        print(f"\nAnalyzing {symbol}...")

        df = self.market.get_market_data(
            symbol,
            DEFAULT_INTERVAL,
        )

        if df is None:
            return None

        market = self.signal_generator.generate(
            symbol,
            df,
        )

        return market