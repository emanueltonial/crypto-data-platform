
from app.repositories.trade_repository import TradeRepository


class TradeService:
    def __init__(self, repository: TradeRepository) -> None:
        self.__repository = repository

    async def bulk_insert_trades(self, trades: list[dict]) -> int:
        if not trades: 
            return 0
        
        return await self.__repository.bulk_insert(trades)