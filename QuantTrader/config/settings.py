APP_NAME = "QuantTrader PRO X"
VERSION = "3.0"

BASE_URL = "https://data-api.binance.vision/api/v3"
REQUEST_TIMEOUT = 10

DEFAULT_INTERVAL = "15m"
DEFAULT_LIMIT = 500

# لیست منتخب: عمدتاً سهام/کالا/شاخص آمریکا (RWA) + فقط سه کریپتوی اصلی
SYMBOLS = [
    # --- کریپتو (فقط ۳ تای اصلی) ---
    "BTC",
    "ETH",
    "HYPE",

    # --- سهام بزرگ تکنولوژی ---
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "AVGO",
    "TSM",
    "ORCL",
    "IBM",
    "AMD",
    "QCOM",
    "DELL",
    "INTC",
    "ARM",
    "ASML",
    "MU",
    "MRVL",
    "NOW",

    # --- خودرو / کریپتو-مرتبط / فین‌تک ---
    "TSLA",
    "COIN",
    "HOOD",
    "MSTR",
    "BABA",

    # --- شرکت‌های نوظهور / پرنوسان ---
    "GME",
    "RKLB",
    "CRCL",
    "CRWV",
    "BB",
    "BE",
    "BIO",
    "S",
    "TTWO",
    "PLTR",
    "XIAOMI",
    "TENCENT",
    "ZHIPU",
    "NBIS",
    "GEV",
    "CHIP",
    "KIOXIA",

    # --- شاخص‌های آمریکا ---
    "SPX",
    "QQQ",
    "IWM",
    "US100",

    # --- کالاها ---
    "XAU",
    "XAG",
    "WTI",
    "BRENTOIL",
    "NATGAS",
    "XCU",
    "WHEAT",
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
