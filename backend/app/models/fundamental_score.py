from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class FundamentalScore(Base):
    """Piotroski F-Score 및 재무 분석 결과"""

    __tablename__ = "fundamental_scores"

    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Piotroski F-Score
    f_score = Column(Integer, nullable=False)  # 0-9점
    max_score = Column(Integer, default=9, nullable=False)

    # F-Score 세부 항목
    score_details = Column(JSON, nullable=True)  # 9가지 항목 상세 정보

    # 주요 재무 지표
    market_cap = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    roa = Column(Float, nullable=True)
    profit_margin = Column(Float, nullable=True)
    operating_margin = Column(Float, nullable=True)
    gross_margin = Column(Float, nullable=True)

    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    symbol = relationship("Symbol", back_populates="fundamental_scores")
    trading_signals = relationship(
        "TradingSignal", back_populates="fundamental_score", cascade="all, delete-orphan"
    )
