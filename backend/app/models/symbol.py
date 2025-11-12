from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)  # e.g., "AAPL"
    name = Column(String, nullable=False)  # e.g., "Apple Inc."
    exchange = Column(String, nullable=True)  # e.g., "NASDAQ"
    currency = Column(String, default="USD")
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    fundamental_scores = relationship(
        "FundamentalScore", back_populates="symbol", cascade="all, delete-orphan"
    )
    trading_signals = relationship(
        "TradingSignal", back_populates="symbol", cascade="all, delete-orphan"
    )
