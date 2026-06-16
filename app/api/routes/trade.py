from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_trade_service
from app.schema.trade import TradeRead
from app.services.trade_service import TradeService

router = APIRouter(prefix="/trades", tags=["trades"])

TradeServiceDep = Annotated[TradeService, Depends(get_trade_service)]


@router.get("/")
async def list_trades(
    service: TradeServiceDep,
    symbol: Annotated[str, Query(description="Trading Symbol (e.g. BTCUSDT)")],
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,  
) -> list[TradeRead]:
    trades = await service.get_trades_by_symbol(symbol.upper(), limit)
    return [TradeRead.model_validate(trade) for trade in trades]