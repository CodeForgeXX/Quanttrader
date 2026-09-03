"""
Provider برای گرفتن داده مستقیم از صرافی Lighter (به‌جای Binance).

این نسخه‌ی اصلاح‌شده‌ست - نسبت به نسخه‌ی اول این تغییرات انجام شده:
  ۱. نرمال‌سازی نماد: به‌جای فقط strip کردن پسوند USDT/USDC/USD، از روی جداکننده‌ی
     "/" یا "-" می‌بریم (دقیقاً همون فیکسی که برای ربات تلگرام هم انجام شد) - چون
     نمادهایی مثل "AAVE/USDC" با روش قبلی به "AAVE/" (با اسلش باقیمونده) تبدیل
     می‌شدن، نه "AAVE" تمیز.
  ۲. فیلتر market_type == "perp" برداشته شد - چون مطمئن نیستیم سهام/فارکس/کالا هم
     زیر همین market_type دسته‌بندی می‌شن یا نه؛ برای اینکه چیزی بی‌سروصدا از
     دست نره، همه‌ی بازارهای فعال رو نگه می‌داریم (فقط status=="active" چک می‌شه).
  ۳. مقاومت در برابر خطای موقت Lighter اضافه شد: هم "Too Many Requests" (نرخ
     محدود) هم مسدودسازی موقت AWS WAF - هردو رو دیده بودیم موقع تست ربات تلگرام؛
     الان چندبار با فاصله دوباره امتحان می‌شه قبل از تسلیم شدن.

نیاز به نصب پکیج توی requirements.txt همین ریپو: lighter-sdk==1.1.2
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

_WAF_MARKERS = ("captcha", "awswaf", "javascript is disabled", "verify that you're not a robot")
_RATE_LIMIT_MARKERS = ("too many requests", '"code":23000', "429")


def _looks_like_waf_block(error) -> bool:
    return any(m in str(error).lower() for m in _WAF_MARKERS)


def _looks_like_rate_limit(error) -> bool:
    return any(m in str(error).lower() for m in _RATE_LIMIT_MARKERS)


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
        """
        'AAVE/USDC' -> 'AAVE', 'ETH-USDC' -> 'ETH', ولی 'EURUSD'/'USDJPY' (فارکس
        بدون جداکننده که خودشون کلمه USD توشونه) دست‌نخورده می‌مونن.
        ⚠️ عمداً پسوند USDT/USDC/USD رو از نمادهای بدون جداکننده strip نمی‌کنیم -
        چون طبق داده‌ی واقعی Lighter (که با ربات تلگرام تستش کردیم)، این صرافی
        یا از جداکننده استفاده می‌کنه یا اصلاً پسوندی نداره؛ فرمت بایننسی مثل
        "BTCUSDT" (بدون جداکننده) روی Lighter دیده نشده.
        """
        base = symbol.upper()
        import re
        parts = re.split(r"[/\-]", base)
        return parts[0].strip() if len(parts) > 1 else base

    def _fetch_with_retry(self, fn, what: str, retries: int = 3):
        """
        fn یه تابع async بدون آرگومانه که باید صدا زده بشه. اگه خطای موقت (نرخ
        محدود یا مسدودسازی AWS) بود، چندبار با فاصله دوباره امتحان می‌کنه.
        """
        last_error = None
        for attempt in range(retries + 1):
            try:
                return asyncio.run(fn())
            except Exception as e:
                last_error = e
                if _looks_like_rate_limit(e):
                    delay = 20.0 * (attempt + 1)
                    logger.warning(f"Lighter نرخ‌محدود کرده برای {what}، {delay:.0f}s صبر می‌کنیم...")
                elif _looks_like_waf_block(e):
                    delay = 10.0 * (2 ** attempt)
                    logger.warning(f"Lighter موقتاً بلاک کرده برای {what}، {delay:.0f}s صبر می‌کنیم...")
                else:
                    # خطای دیگه (نه rate-limit نه WAF) - همون‌جا تسلیم می‌شیم، تکرار فایده نداره
                    raise
                if attempt < retries:
                    time.sleep(delay)
                    continue
                raise last_error

    def _refresh_markets(self):
        async def _fetch():
            client = lighter.ApiClient(lighter.Configuration(host=self.base_url))
            order_api = lighter.OrderApi(client)
            resp = await order_api.order_books()
            await client.close()
            return resp

        try:
            resp = self._fetch_with_retry(_fetch, "لیست بازارها")
        except Exception as e:
            logger.error(f"گرفتن لیست بازارهای Lighter ناموفق بود: {e}")
            return

        mapping = {}
        for book in resp.order_books:
            if getattr(book, "status", "active") != "active":
                continue
            symbol = getattr(book, "symbol", None)
            market_id = getattr(book, "market_id", None)
            if symbol is None or market_id is None:
                continue
            alias = self._normalize_symbol(symbol)
            if alias:
                mapping[alias] = market_id

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
            resp = self._fetch_with_retry(_fetch, f"کندل‌های {symbol}")
        except Exception as e:
            logger.error(f"Lighter request failed for {symbol}: {e}")
            return None

        candles = getattr(resp, "c", None)
        if not candles:
            logger.error(f"Lighter returned empty data for {symbol}")
            return None

        rows = []
        for c in sorted(candles, key=lambda x: getattr(x, "t", 0)):
            rows.append(
                [
                    getattr(c, "t", None),
                    getattr(c, "o", None),
                    getattr(c, "h", None),
                    getattr(c, "l", None),
                    getattr(c, "c", None),
                    getattr(c, "v", 0),
                ]
            )

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
