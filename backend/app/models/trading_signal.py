from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class TradingSignal(Base):
    """하이브리드 매매 시그널"""

    __tablename__ = "trading_signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    fundamental_score_id = Column(
        Integer, ForeignKey("fundamental_scores.id"), nullable=True
    )
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 시그널 정보
    signal_type = Column(
        String(20), nullable=False, index=True
    )  # strong_buy, buy, hold, warning, sell, strong_sell
    signal_strength = Column(
        String(20), nullable=False
    )  # very_strong, strong, moderate, weak

    # 가격 정보
    current_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)  # 목표가
    stop_loss = Column(Float, nullable=True)  # 손절가

    # 조건 체크 결과
    conditions = Column(JSON, nullable=True)  # 조건별 충족 여부

    # 추천 사항
    recommendations = Column(JSON, nullable=True)  # 추천 액션 리스트

    # 리스크 평가
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    risk_factors = Column(JSON, nullable=True)  # 리스크 요인 리스트

    # 시그널 활성화 여부
    is_active = Column(Boolean, default=True, nullable=False)

    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    symbol = relationship("Symbol", back_populates="trading_signals")
    fundamental_score = relationship("FundamentalScore", back_populates="trading_signals")
