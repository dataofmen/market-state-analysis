from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional
from app.schemas.symbol import SymbolResponse, TechnicalIndicatorResponse, MarketStateResponse


class WatchlistItemBase(BaseModel):
    symbol_id: int
    notes: Optional[str] = None


class WatchlistItemCreate(WatchlistItemBase):
    pass


class WatchlistItemUpdate(BaseModel):
    notes: Optional[str] = None


class WatchlistItemResponse(WatchlistItemBase):
    id: int
    user_id: UUID4
    added_at: datetime

    class Config:
        from_attributes = True


class WatchlistItemDetailResponse(BaseModel):
    """관심 종목 상세 정보 (심볼 정보 + 최신 지표 + 시장 상태 포함)"""
    id: int
    user_id: UUID4
    added_at: datetime
    notes: Optional[str] = None
    symbol: SymbolResponse
    current_price: Optional[float] = None
    latest_indicator: Optional[TechnicalIndicatorResponse] = None
    latest_market_state: Optional[MarketStateResponse] = None

    class Config:
        from_attributes = True
