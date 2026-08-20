APP_NAME = "QuantTrader PRO X"
VERSION = "3.0"

BASE_URL = "https://data-api.binance.vision/api/v3"
REQUEST_TIMEOUT = 10

DEFAULT_INTERVAL = "15m"
DEFAULT_LIMIT = 500

# لیست منتخب: بهترین‌های بازار RWA (سهام بزرگ، شاخص‌ها، کالاها) + چند کریپتوی اصلی روی Lighter
SYMBOLS = [
    # --- سهام بزرگ آمریکا ---
    "AAPL",   # اپل
    "MSFT",   # مایکروسافت
    "GOOGL",  # گوگل
    "AMZN",   # آمازون
    "NVDA",   # انویدیا
    "TSLA",   # تسلا
    "META",   # متا
    "AVGO",   # Broadcom
    "TSM",    # TSMC
    "ORCL",   # اوراکل
    "IBM",
    "AMD",
    "QCOM",   # کوالکام
    "COIN",   # Coinbase
    "HOOD",   # Robinhood
    "PLTR",   # Palantir
    "MSTR",   # MicroStrategy
    "BABA",   # علی‌بابا

    # --- شاخص‌های آمریکا ---
    "SPX",    # S&P 500
    "QQQ",    # Nasdaq ETF

    # --- کالاها ---
    "XAU",    # طلا
    "XAG",    # نقره
    "WTI",    # نفت
    "NATGAS", # گاز طبیعی

    # --- کریپتوهای اصلی ---
    "BTC",
    "ETH",
    "SOL",
    "BNB",
    "XRP",
    "DOGE",
    "ADA",
    "AVAX",
]

TIMEFRAMES = [
    "5m",
    "15m",
    "1h",
    "4h",
]

EMA_FAST = 20
EMA_MID = 50
EMA_SLOW = 200

# Legacy indicator settings (used by src/dashboard_data.py)
SMA_PERIOD = 20
EMA_PERIOD = 20
RSI_PERIOD = 14

# Risk management settings (used by src/core/risk_manager.py, src/dashboard_data.py)
ACCOUNT_BALANCE = 10000
RISK_PERCENT = 1
