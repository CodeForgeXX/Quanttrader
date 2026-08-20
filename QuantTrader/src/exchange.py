from src.providers import BinanceProvider
from src.providers.lighter import LighterProvider


class ExchangeManager:
    """
    مدیریت اتصال به صرافی‌ها
    """

    def __init__(self, provider="lighter"):
        if provider.lower() == "binance":
            self.provider = BinanceProvider()
        elif provider.lower() == "lighter":
            self.provider = LighterProvider()
        else:
            raise ValueError(
                f"Provider '{provider}' is not supported."
            )

    def get_klines(
        self,
        symbol,
        interval=None,
        limit=None,
    ):
        return self.provider.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
        )

    def get_symbols(self):
        return self.provider.get_symbols()
