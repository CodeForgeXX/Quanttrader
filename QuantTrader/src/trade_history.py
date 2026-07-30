import os
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(file)))
FILE_PATH = os.path.join(BASE_DIR, "data", "trades.csv")
MAX_ROWS = 500


def save_trade(symbol, price, signal, score, probability):

    trade = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Coin": symbol,
        "Price": price,
        "Signal": signal,
        "Score": score,
        "Probability": probability,
    }

    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
    else:
        df = pd.DataFrame(
            columns=[
                "Time",
                "Coin",
                "Price",
                "Signal",
                "Score",
                "Probability",
            ]
        )

    df = pd.concat([df, pd.DataFrame([trade])], ignore_index=True)

    # Keep only the most recent MAX_ROWS entries so the file (and the
    # read/rewrite cost on every save) doesn't grow forever under
    # continuous 24/7 operation.
    if len(df) > MAX_ROWS:
        df = df.tail(MAX_ROWS)

    df.to_csv(FILE_PATH, index=False)
