from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trade import Trade


class TradeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def bulk_insert(self, trades: list[dict]) -> int: # pyright: ignore[reportReturnType]
        """Persists a list of normalized trades to the database.

        Inserts new records and skips existing ones based on trade_id conflict.
        Skips execution if the list is empty.

        Args:
            trades: List of dicts with keys matching the Trade model columns.

        Returns:
            Number of records sent to the database (inserted + skipped).
        """
        if not trades:
            return 0
        
        stmt = ( 
            insert(Trade)
            .values(trades)
            .on_conflict_do_nothing( 
                index_elements=["trade_id"],
            )
        )

        await self.__session.execute(stmt)
        await self.__session.commit()

        return len(trades)