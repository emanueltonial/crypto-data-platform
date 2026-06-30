from datetime import UTC, datetime, timezone  # noqa: F401
from decimal import Decimal  # noqa: F401

from httpx import AsyncClient  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: F401

from app.models.trade import Trade  # noqa: F401
from tests.api_client import HealthApiClient, TradeApiClient  # noqa


async def insert_trade(session: AsyncSession, **kwargs):
    defaults = {
    "trade_id": 1001,
    "symbol": "BTCUSDT",
    "price": Decimal("65000.12345678"),
    "quantity": Decimal("0.00100000"),
    "quote_quantity": Decimal("65.00012345"),
    "time": datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
    "is_buyer_maker": False,
    "is_best_match": True,
    }

    defaults.update(kwargs)
    trade = Trade(**defaults)
    session.add(trade)
    await session.flush()
    return trade


# health endpoint
async def test_health_status_200(client: AsyncClient):
    response = await HealthApiClient(client).check()
    assert response.status_code == 200


async def test_health_body(client: AsyncClient):
    response = await HealthApiClient(client).check()
    assert response.json() == {"status": "ok"}


# happy results
async def test_list_trades_status_200(client: AsyncClient, db_session: AsyncSession):
    await insert_trade(db_session, trade_id=2001, symbol="BTCUSDT")
    response = await TradeApiClient(client).list_trades("BTCUSDT")
    assert response.status_code == 200


    await insert_trade(db_session, trade_id=2002, symbol="BTCUSDT")
    data = (await TradeApiClient(client).list_trades("BTCUSDT")).json()
    assert data and all(s["symbol"] == "BTCUSDT" for s in data)


async def test_list_trades_excludes_other_symbols(client: AsyncClient, db_session: AsyncSession): # noqa: E501
    await insert_trade(db_session, trade_id=2003, symbol="BTCUSDT")
    await insert_trade(db_session, trade_id=2004, symbol="ETHUSDT")
    data = (await TradeApiClient(client).list_trades("BTCUSDT")).json()
    assert all(t["symbol"] == "BTCUSDT" for t in data)


async def test_list_trades_returns_schema_fields(client: AsyncClient, db_session: AsyncSession):  # noqa: E501
    await insert_trade(db_session, trade_id=2005, symbol="BTCUSDT")
    data = (await TradeApiClient(client).list_trades("BTCUSDT")).json()
    expected = {
        "id", "trade_id", "symbol", "price", "quantity",
        "quote_quantity", "time", "is_buyer_maker", "is_best_match",
    }
    assert expected.issubset(data[0].keys())


async def test_list_trades_symbol_case_insensitive(client: AsyncClient, db_session: AsyncSession): # noqa: E501
    # Router uses symbol.upper(), so lower case must works
    await insert_trade(db_session, trade_id=2006, symbol="BTCUSDT")
    response = await TradeApiClient(client).list_trades("btcusdt")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_list_trades_empty_for_unknown_symbol(client: AsyncClient):
    data = (await TradeApiClient(client).list_trades("SOLUSDT")).json()
    assert data == []


# Testing API rate limit
async def test_list_trades_respects_limit(client: AsyncClient, db_session: AsyncSession):  # noqa: E501
    for i in range(5):
        await insert_trade(db_session, trade_id=4000 + i, symbol="ETHUSDT")
    data = (await TradeApiClient(client).list_trades("ETHUSDT", limit=2)).json()
    assert len(data) <= 2


async def test_list_trades_limit_zero_rejected(client: AsyncClient):
    # Router declares ge=1 -> 0 fails validation.
    response = await TradeApiClient(client).list_trades_raw(symbol="BTCUSDT", limit=0)
    assert response.status_code == 422


async def test_list_trades_limit_too_high_rejected(client: AsyncClient):
    # Router declares le=1000 -> 1001 fails validation.
    response = await TradeApiClient(client).list_trades_raw(symbol="BTCUSDT", limit=1001)  # noqa: E501
    assert response.status_code == 422
