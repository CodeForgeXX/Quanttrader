import logging
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("QuantTrader")
logger.setLevel(logging.INFO)

# جلوگیری از اضافه شدن چندباره‌ی handler (وقتی streamlit فایل رو دوباره اجرا می‌کنه)
if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # نوشتن لاگ در فایل
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, "quanttrader.log")
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # نوشتن لاگ در کنسول (stdout) تا در Streamlit Cloud logs هم دیده بشه
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
