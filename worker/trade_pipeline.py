import asyncio
import logging
from pathlib import Path

import httpx
import pandas as pd

from app.core.database import AsyncSessionLocal
from app.core.logging import setup_logging
from app.core.settings import settings
from app.services.trade_service import TradeService

logger = logging.getLogger("crypto-data-platform.worker.trade_pipeline")

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


class BinanceWorker:
    """Worker responsible for fetching, transforming, and saving trade data from Binance."""  # noqa: E501

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(base_url=settings.binance_base_url, timeout=10)

    async def fetch_data(
        self, endpoint: str, params: dict[str, str | int] | None = None
    ) -> list | None:
        logger.info(f"Starting request | endpoint={endpoint} | params={params}")
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            logger.info(f"Request finished | status={response.status_code}")
            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout accessing {endpoint}")
        except httpx.ConnectError:
            logger.error(f"Connection error accessing {endpoint}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error | status={e.response.status_code} | body={e.response.text}")  # noqa: E501
        except Exception:
            logger.exception("Unexpected error in fetch_data")
        return None

    async def transform(self, raw_data: list, symbol: str) -> list[dict]:
        logger.info(f"Starting transformation | symbol={symbol} | records={len(raw_data)}") # noqa: E501
        
        df = pd.DataFrame(raw_data)
        df["price"] = df["price"].astype(float)
        df["qty"] = df["qty"].astype(float)
        df["quoteQty"] = df["quoteQty"].astype(float)
        df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
        df = df.rename(columns={
            "id": "trade_id",
            "qty": "quantity",
            "quoteQty": "quote_quantity",
            "isBuyerMaker": "is_buyer_maker",
            "isBestMatch": "is_best_match",
        })
        df["symbol"] = symbol
        
        logger.info(f"Transformation finished | symbol={symbol} | shape={df.shape}")
        return df.to_dict(orient="records")

    async def persist(self, trades: list[dict], symbol: str) -> None:
        async with AsyncSessionLocal() as session:
            service = TradeService(session)
            inserted = await service.bulk_insert_trades(trades)
            
            logger.info(f"Data persisted | symbol={symbol} | records={inserted}")

    async def run(self) -> None:
        logger.info("Ingestion started")
        total_records = 0
        try:
            for symbol in settings.binance_symbols:
                raw = await self.fetch_data(
                    "/trades",
                    params={"symbol": symbol, "limit": settings.binance_limit},
                )
                if raw is None:
                    logger.warning(f"No data for {symbol}. Skipping.")
                    continue
                
                trades = await self.transform(raw, symbol)
                await self.persist(trades, symbol)
                total_records += len(trades)

                logger.info(f"Ingestion finished | total_records={total_records}")
        finally:
            await self.client.aclose()


if __name__ == "__main__":
    setup_logging()
    worker = BinanceWorker()
    asyncio.run(worker.run())