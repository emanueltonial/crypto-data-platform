"""
Unit tests — BinanceWorker.transform()

Pure logic. No DB, no HTTP. We feed a raw Binance payload and assert the
output dict matches the Trade model's column names and types.
"""

import pandas as pd
import pytest

from worker.trade_pipeline import BinanceWorker

SYMBOL = "BTCUSDT"

# Raw shape exactly as Binance /trades returns it (camelCase, string numbers, ms time).
RAW_TRADE = {
    "id": 123456,
    "price": "65000.12345678",
    "qty": "0.00100000",
    "quoteQty": "65.00012345",
    "time": 1_700_000_000_000,
    "isBuyerMaker": True,
    "isBestMatch": True,
}


@pytest.fixture()
def worker() -> BinanceWorker:
    return BinanceWorker()


async def test_renames_id_to_trade_id(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert "trade_id" in result[0] and "id" not in result[0]


async def test_renames_qty_to_quantity(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert "quantity" in result[0] and "qty" not in result[0]


async def test_renames_quoteqty_to_quote_quantity(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert "quote_quantity" in result[0] and "quoteQty" not in result[0]


async def test_renames_isbuyermaker(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert "is_buyer_maker" in result[0] and "isBuyerMaker" not in result[0]


async def test_renames_isbestmatch(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert "is_best_match" in result[0] and "isBestMatch" not in result[0]


async def test_price_cast_to_float(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert isinstance(result[0]["price"], float)


async def test_quantity_cast_to_float(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert isinstance(result[0]["quantity"], float)


async def test_quote_quantity_cast_to_float(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert isinstance(result[0]["quote_quantity"], float)


async def test_time_is_tz_aware_timestamp(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    t = result[0]["time"]
    assert isinstance(t, pd.Timestamp)
    assert t.tzinfo is not None


# --- symbol injection --------------------------------------------------------

async def test_injects_symbol(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert result[0]["symbol"] == SYMBOL


async def test_symbol_not_uppercased_inside_transform(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], "btcusdt")
    assert result[0]["symbol"] == "btcusdt"


async def test_returns_list_of_dicts(worker: BinanceWorker):
    result = await worker.transform([RAW_TRADE], SYMBOL)
    assert isinstance(result, list) and isinstance(result[0], dict)


async def test_preserves_record_count(worker: BinanceWorker):
    raw = [dict(RAW_TRADE, id=i) for i in range(5)]
    result = await worker.transform(raw, SYMBOL)
    assert len(result) == 5