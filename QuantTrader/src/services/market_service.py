import requests
import pandas as pd

from config.settings import (
    BASE_URL,
    REQUEST_TIMEOUT,
    DEFAULT_LIMIT,
)


class MarketService:

    def __init__(self):
        pass

    def get_market_data(
        self,
        symbol,
        interval,
        limit=DEFAULT_LIMIT,
    ):

        try:

            url = f"{BASE_URL}/klines"

            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
            }

            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            df = pd.DataFrame(
                data,
                columns=[
                    "OpenTime",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "CloseTime",
                    "QuoteAssetVolume",
                    "Trades",
                    "TakerBase",
                    "TakerQuote",
                    "Ignore",
                ],
            )

            numeric = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]

            df[numeric] = df[numeric].astype(float)

            return df

        except Exception as e:

            print(f"Market Error -> {symbol} {interval}")

            print(e)

            return None

    def get_multi_timeframe_data(
        self,
        symbol,
        timeframes,
    ):

        result = {}

        for timeframe in timeframes:

            df = self.get_market_data(
                symbol,
                timeframe,
            )

            if df is not None:

                result[timeframe] = df

        return result