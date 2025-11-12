from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Dict, Any


class SymbolBase(BaseModel):
    symbol: str
    name: str
    exchange: str


class SymbolCreate(SymbolBase):
    pass


class SymbolResponse(SymbolBase):
    id: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class TechnicalIndicatorResponse(BaseModel):
    """기술적 지표 응답"""
    date: date
    atr: Optional[float] = None
    atr_ratio: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_width_ratio: Optional[float] = None
    adx: Optional[float] = None
    plus_di: Optional[float] = None
    minus_di: Optional[float] = None
    std_dev: Optional[float] = None
    vix: Optional[float] = None

    class Config:
        from_attributes = True


class MarketStateResponse(BaseModel):
    """시장 상태 분류 응답"""
    date: date
    trend_type: str  # uptrend, downtrend, range
    volatility_level: str  # low, normal, high, extreme
    risk_level: str  # stable, caution, alert, danger
    recommended_strategy: str
    position_sizing_ratio: float
    reasoning: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SymbolDetailResponse(BaseModel):
    """심볼 상세 정보 (지표 + 시장 상태 포함)"""
    symbol: SymbolResponse
    current_price: Optional[float] = None
    latest_indicator: Optional[TechnicalIndicatorResponse] = None
    latest_market_state: Optional[MarketStateResponse] = None

    class Config:
        from_attributes = True


class SymbolSearchResponse(BaseModel):
    """심볼 검색 결과"""
    symbol: str
    name: str
    exchange: str
    currency: Optional[str] = None
    stock_type: Optional[str] = None
