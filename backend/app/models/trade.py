from sqlalchemy import Column, Integer, ForeignKey, Date, String, Numeric, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol_id = Column(Integer, ForeignKey("symbols.id", ondelete="CASCADE"), nullable=False)

    # Trade Details
    trade_type = Column(String, nullable=False)  # 'buy' or 'sell'
    entry_date = Column(Date, nullable=False)
    exit_date = Column(Date, nullable=True)
    entry_price = Column(Numeric(10, 4), nullable=False)
    exit_price = Column(Numeric(10, 4), nullable=True)
    quantity = Column(Integer, nullable=False)

    # Performance Metrics
    profit_loss = Column(Numeric(12, 2), nullable=True)
    profit_loss_percent = Column(Numeric(8, 4), nullable=True)

    # Strategy & Notes
    strategy_used = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    symbol = relationship("Symbol")
