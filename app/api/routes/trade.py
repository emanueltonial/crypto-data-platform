from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_trade_service
from app.schema.trade import Trade as TradeDTO
from app.services.trade_service import TradeService

router = APIRouter(prefix="/trades", tags=["trades"])

@router.get("/")
async def list_trades(
    symbol: Annotated[str, Query(description="Trading Symbol (e.g. BTCUSDT)")],
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    service: TradeService = Depends(get_trade_service),  # noqa: B008, FAST002
) -> list[TradeDTO]:
    trades = await service.get_trades_by_symbol(symbol.upper(), limit)
    return [TradeDTO.model_validate(trade) for trade in trades]