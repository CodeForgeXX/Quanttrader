APP_NAME = "QuantTrader PRO X"
VERSION = "3.0"

BASE_URL = "https://data-api.binance.vision/api/v3"

REQUEST_TIMEOUT = 10
DEFAULT_INTERVAL = "15m"
DEFAULT_LIMIT = 500
SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
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
