"""
Provider جدید برای گرفتن داده مستقیم از صرافی Lighter (به‌جای Binance).
این فایل رو توی مسیر QuantTrader/src/providers/lighter.py ریپو اضافه کن.

نیاز به نصب پکیج جدید توی requirements.txt همین ریپو: lighter-sdk
"""

import asyncio
import time

import pandas as pd
import lighter

from src.logger import logger

LIGHTER_BASE_URL = "https://mainnet.zklighter.elliot.ai"
MARKET_CACHE_TTL = 300  # ثانیه - هر ۵ دقیقه لیست بازارها رو دوباره می‌خونه

RESOLUTION_MAP = {
    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    "1h": "1h", "4h": "4h", "1d": "1d", "1D": "1d",
}
STEP_SECONDS = {
    "1m": 60, "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "4h": 14400, "1d": 86400,
}


class LighterProvider:
    """
    همون اینترفیس BaseProvider (get_klines, get_symbols, get_ticker) رو پیاده‌سازی می‌کنه،
    ولی داده رو از Lighter می‌خونه به‌جای Binance.
    """

    def __init__(self, base_url: str = LIGHTER_BASE_URL):
        self.base_url = base_url
        self._market_cache = {}
        self._market_cache_time = 0.0

    # ---------- کمکی: نگاشت symbol -> market_index ----------

    def _normalize_symbol(self, symbol: str) -> str:
        """'BTCUSDT' -> 'BTC' چون Lighter از فرمت بدون USDT استفاده می‌کنه."""
        base = symbol.upper()
        for suffix in ("USDT", "USDC", "USD"):
            if base.endswith(suffix) and len(base) > len(suffix):
                return base[: -len(suffix)]
        return base

    def _refresh_markets(self):
        async def _fetch():
            client = lighter.ApiClient(lighter.Configuration(host=self.base_url))
            order_api = lighter.OrderApi(client)
            resp = await order_api.order_books()
            await client.close()
            return resp

        resp = asyncio.run(_fetch())
        mapping = {}
        for book in resp.order_books:
            if getattr(book, "market_type", "perp") != "perp":
                continue
            if getattr(book, "status", "active") != "active":
                continue
            symbol = getattr(book, "symbol", None)
            market_id = getattr(book, "market_id", None)
            if symbol is not None and market_id is not None:
                mapping[symbol.upper()] = market_id

        self._market_cache = mapping
        self._market_cache_time = time.time()

    def _get_market_index(self, symbol: str):
        if not self._market_cache or (time.time() - self._market_cache_time) > MARKET_CACHE_TTL:
            self._refresh_markets()
        return self._market_cache.get(self._normalize_symbol(symbol))

    # ---------- اینترفیس اصلی ----------

    def get_klines(self, symbol, interval=None, limit=None):
        market_index = self._get_market_index(symbol)
        if market_index is None:
            logger.error(f"Lighter: symbol {symbol} توی لیست بازارها پیدا نشد.")
            return None

        resolution = RESOLUTION_MAP.get(interval, "15m")
        step = STEP_SECONDS.get(resolution, 900)
        count = limit or 500
        end_ts = int(time.time())
        start_ts = end_ts - step * count

        async def _fetch():
            client = lighter.ApiClient(lighter.Configuration(host=self.base_url))
            candlestick_api = lighter.CandlestickApi(client)
            resp = await candlestick_api.candles(
                market_id=market_index,
                resolution=resolution,
                start_timestamp=start_ts,
                end_timestamp=end_ts,
                count_back=count,
            )
            await client.close()
            return resp

        try:
            resp = asyncio.run(_fetch())
        except Exception as e:
            logger.error(f"Lighter request failed for {symbol}: {e}")
            return None

        candles = getattr(resp, "c", None) or getattr(resp, "candles", None) or getattr(resp, "candlesticks", None)
        if not candles:
            logger.error(f"Lighter returned empty data for {symbol}")
            return None

        rows = []
        for c in sorted(candles, key=lambda x: getattr(x, "timestamp", getattr(x, "t", 0))):
            ts = getattr(c, "timestamp", getattr(c, "t", None))
            o = getattr(c, "open", getattr(c, "o", None))
            h = getattr(c, "high", getattr(c, "h", None))
            l = getattr(c, "low", getattr(c, "l", None))
            cl = getattr(c, "close", getattr(c, "c", None))
            v = getattr(c, "volume0", getattr(c, "volume", getattr(c, "v", 0)))
            rows.append([ts, o, h, l, cl, v])

        df = pd.DataFrame(rows, columns=["Open Time", "Open", "High", "Low", "Close", "Volume"])
        df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
        df["Open Time"] = pd.to_datetime(df["Open Time"], unit="s")
        df.set_index("Open Time", inplace=True)

        logger.info(f"{symbol} loaded from Lighter")
        return df

    def get_symbols(self):
        if not self._market_cache or (time.time() - self._market_cache_time) > MARKET_CACHE_TTL:
            self._refresh_markets()
        return list(self._market_cache.keys())

    def get_ticker(self, symbol):
        raise NotImplementedError("get_ticker برای LighterProvider هنوز پیاده‌سازی نشده - فعلاً استفاده نمی‌شه.")
