from config.settings import (
    DEFAULT_INTERVAL,
    DEFAULT_LIMIT,
)

from src.exchange import ExchangeManager

# فقط یک بار ساخته می‌شود
exchange = ExchangeManager()


def get_klines(
    symbol,
    interval=DEFAULT_INTERVAL,
    limit=DEFAULT_LIMIT,
):
    """
    دریافت داده‌های بازار از Provider فعال
    """

    return exchange.get_klines(
        symbol=symbol,
        interval=interval,
        limit=limit,
    )