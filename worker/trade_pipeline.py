import logging
from pathlib import Path

import pandas as pd
import requests

from app.core.constants import BASE_URL, LIST_SYMBOLS
from app.core.logging import setup_logging

logger = logging.getLogger("crypto_flow.worker.trade_pipeline")

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


class BinanceRequests:
    """Worker responsible for fetching, transforming, and saving trade data from Binance."""  # noqa: E501

    def __init__(self) -> None:
        """Initialize HTTP session."""
        self.session = requests.Session()

    def fetch_data(self, endpoint: str, params: dict[str, str | int] | None = None) -> list | None:  # noqa: E501
        """Fetch raw data from Binance REST API.

        Returns parsed JSON as a list, or None on failure.
        """
        url = BASE_URL + endpoint
        logger.info(f"Starting request | url={url} | params={params}")

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            logger.info(f"Request finished | status={response.status_code}")
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Timeout accessing {url}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error accessing {url}")
        except requests.exceptions.HTTPError:
            logger.error(f"HTTP error | status={response.status_code} | body={response.json()}")  # noqa: E501
        except Exception:
            logger.exception("Unexpected error in fetch_data")

        return None

    def transform(self, raw_data: list) -> pd.DataFrame:
        """Cast types, parse timestamps, and normalize column names.

        Returns a clean DataFrame ready for persistence.
        """
        logger.info(f"Starting transformation | records={len(raw_data)}")

        df = pd.DataFrame(raw_data)

        df["price"] = df["price"].astype(float)
        df["qty"] = df["qty"].astype(float)
        df["quoteQty"] = df["quoteQty"].astype(float)
        df["time"] = pd.to_datetime(df["time"], unit="ms")

        df = df.rename(columns={
            "id": "trade_id",
            "qty": "quantity",
            "quoteQty": "quote_quantity",
            "isBuyerMaker": "is_buyer_maker",
            "isBestMatch": "is_best_match",
        })

        logger.info(f"Transformation finished | shape={df.shape}")
        return df

    def save(self, df: pd.DataFrame, filename: str = "trades.xlsx") -> None:
        """Persist DataFrame to Excel file inside the data/ directory.

        This is a temporary storage strategy — will be replaced by Postgres in a near future.
        """
        filepath = OUTPUT_DIR / filename

        try:
            df.to_excel(filepath, index=False)
            logger.info(f"Data saved | file={filepath} | records={len(df)}")
        except Exception:
            logger.exception(f"Failed to save file {filepath}")

    def run(self) -> None:
        """Execute the full ingestion pipeline: fetch -> transform -> save."""
        logger.info("Ingestion started")

        total_records = 0

        for symbol in LIST_SYMBOLS:
            raw = self.fetch_data("/trades", params={"symbol": symbol, "limit": 50})
            if raw is None:
                logger.warning(f"No data for {symbol}. Skipping.")
                continue
            df = self.transform(raw)
            df["symbol"] = symbol
            self.save(df, filename=f"trades_{symbol}.xlsx")
            total_records += len(df)

        logger.info(f"── Ingestion finished | total_records={total_records} ──")

if __name__ == "__main__":
    setup_logging()
    worker = BinanceRequests()
    worker.run()