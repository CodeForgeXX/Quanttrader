from src.providers import BinanceProvider


class ExchangeManager:
    """
    مدیریت اتصال به صرافی‌ها
    """

    def __init__(self, provider="binance"):

        if provider.lower() == "binance":
            self.provider = BinanceProvider()

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