import requests
import pandas as pd
from config.settings import (
    BASE_URL,
    DEFAULT_INTERVAL,
    DEFAULT_LIMIT,
    REQUEST_TIMEOUT,
)
from src.logger import logger


class BinanceProvider:
    def __init__(self):
        self.base_url = BASE_URL

    def get_klines(
        self,
        symbol,
        interval=DEFAULT_INTERVAL,
        limit=DEFAULT_LIMIT,
    ):
        url = f"{self.base_url}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
        try:
            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.error(
                    f"Binance returned empty data for {symbol} "
                    f"(url={url}, params={params})"
                )
                return None

            df = pd.DataFrame(
                data,
                columns=[
                    "Open Time",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "Close Time",
                    "Quote Asset Volume",
                    "Trades",
                    "Taker Buy Base",
                    "Taker Buy Quote",
                    "Ignore",
                ],
            )
            df[
                [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                ]
            ] = df[
                [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                ]
            ].astype(float)
            df["Open Time"] = pd.to_datetime(
                df["Open Time"],
                unit="ms",
            )
            df.set_index(
                "Open Time",
                inplace=True,
            )
            logger.info(f"{symbol} loaded from Binance")
            return df

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else "?"
            body = e.response.text[:300] if e.response is not None else ""
            logger.error(
                f"Binance HTTP error for {symbol}: status={status_code} "
                f"body={body} url={url}"
            )
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Binance request failed for {symbol}: {e} (url={url})")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol} from Binance: {e}")
            return None
