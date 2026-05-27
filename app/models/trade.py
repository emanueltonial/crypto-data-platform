from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Trade(Base):
    __tablename__="trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trade_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(20,8), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20,8), nullable=False)
    quote_quantity: Mapped[Decimal] = mapped_column(Numeric(20,8), nullable=False)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_buyer_maker: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_best_match: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (
        Index("ix_trades_symbol", "symbol"),
        Index("ix_trades_time", "time"),
        Index("ix_trades_symbol_time", "symbol", "time"),
        )