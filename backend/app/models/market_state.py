from sqlalchemy import Column, Integer, ForeignKey, Date, String, Numeric, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class MarketState(Base):
    __tablename__ = "market_states"

    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)

    # Market State Classification
    trend_type = Column(String, nullable=False)  # 'uptrend', 'downtrend', 'range'
    volatility_level = Column(String, nullable=False)  # 'low', 'normal', 'high', 'extreme'
    risk_level = Column(String, nullable=False)  # 'stable', 'caution', 'alert', 'danger'

    # Strategy Recommendation
    recommended_strategy = Column(String, nullable=False)
    position_sizing_ratio = Column(Numeric(4, 2), nullable=False)  # 0.25 to 2.0

    # Relationships
    symbol = relationship("Symbol")

    # Unique constraint on symbol_id and date
    __table_args__ = (
        Index('idx_market_state_symbol_date', 'symbol_id', 'date', unique=True),
    )
