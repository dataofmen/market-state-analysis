from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)

    # ATR (Average True Range)
    atr = Column(Numeric(10, 4))
    atr_ratio = Column(Numeric(10, 6))  # ATR / Price

    # Bollinger Bands
    bb_upper = Column(Numeric(10, 4))
    bb_middle = Column(Numeric(10, 4))
    bb_lower = Column(Numeric(10, 4))
    bb_width = Column(Numeric(10, 4))
    bb_width_ratio = Column(Numeric(10, 6))  # BB Width / Price

    # ADX (Average Directional Index)
    adx = Column(Numeric(10, 4))
    plus_di = Column(Numeric(10, 4))
    minus_di = Column(Numeric(10, 4))

    # VIX (for market-wide volatility)
    vix = Column(Numeric(10, 4), nullable=True)

    # Standard Deviation
    std_dev = Column(Numeric(10, 4))

    # Relationships
    symbol = relationship("Symbol")

    # Unique constraint on symbol_id and date
    __table_args__ = (
        Index('idx_symbol_date', 'symbol_id', 'date', unique=True),
    )
