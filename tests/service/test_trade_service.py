
from datetime import UTC, datetime
from decimal import Decimal

from app.models.trade import Trade
from app.services.trade_service import TradeService


class FakeTradeRepository:
    """Same method surface as the real TradeRepository, backed by a list."""

    def __init__(self, existing: list[Trade] | None = None) -> None:
        self._trades = existing or []
        self.last_inserted: list[dict] = []
        self.insert_called = False

    async def get_by_symbol(self, symbol: str, limit: int) -> list[Trade]:
        matches = [t for t in self._trades if t.symbol == symbol]
        return matches[:limit]

    async def bulk_insert(self, trades: list[dict]) -> int:
        self.insert_called = True
        self.last_inserted = trades
        return len(trades)


def make_trade(**kwargs) -> Trade:
    """Build a Trade ORM instance in memory without a DB round-trip."""
    defaults = {
        "id": 1,
        "trade_id": 1001,
        "symbol": "BTCUSDT",
        "price": Decimal("65000.00000000"),
        "quantity": Decimal("0.00100000"),
        "quote_quantity": Decimal("65.00000000"),
        "time": datetime(2024, 1, 1, tzinfo=UTC),
        "is_buyer_maker": False,
        "is_best_match": True,
    }
    defaults.update(kwargs)
    return Trade(**defaults)


async def test_returns_only_requested_symbol():
    btc = make_trade(id=1, trade_id=1, symbol="BTCUSDT")
    eth = make_trade(id=2, trade_id=2, symbol="ETHUSDT")
    service = TradeService(FakeTradeRepository([btc, eth]))

    result = await service.get_trades_by_symbol("BTCUSDT", 10)

    assert len(result) == 1
    assert result[0].symbol == "BTCUSDT"


async def test_returns_empty_when_no_match():
    service = TradeService(FakeTradeRepository([]))
    assert await service.get_trades_by_symbol("SOLUSDT", 10) == []


async def test_respects_limit():
    trades = [make_trade(id=i, trade_id=i, symbol="BTCUSDT") for i in range(10)]
    service = TradeService(FakeTradeRepository(trades))

    result = await service.get_trades_by_symbol("BTCUSDT", 3)

    assert len(result) == 3



async def test_bulk_insert_returns_count():
    service = TradeService(FakeTradeRepository())
    trades = [{"trade_id": i, "symbol": "BTCUSDT"} for i in range(5)]
    assert await service.bulk_insert_trades(trades) == 5


async def test_bulk_insert_empty_returns_zero():
    service = TradeService(FakeTradeRepository())
    assert await service.bulk_insert_trades([]) == 0


async def test_bulk_insert_empty_skips_repository():
    repo = FakeTradeRepository()
    service = TradeService(repo)
    await service.bulk_insert_trades([])
    assert repo.insert_called is False


async def test_bulk_insert_forwards_payload():
    repo = FakeTradeRepository()
    service = TradeService(repo)
    trades = [{"trade_id": 99, "symbol": "ETHUSDT"}]
    await service.bulk_insert_trades(trades)
    assert repo.last_inserted == trades