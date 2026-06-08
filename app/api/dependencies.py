
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.trade_repository import TradeRepository
from app.services.trade_service import TradeService


async def get_trade_service(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> TradeService:
    return TradeService(TradeRepository(session))

