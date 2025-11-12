from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.watchlist import Watchlist
from app.models.symbol import Symbol
from app.models.technical_indicator import TechnicalIndicator
from app.models.market_state import MarketState
from app.schemas.watchlist import (
    WatchlistItemResponse,
    WatchlistItemCreate,
    WatchlistItemUpdate,
    WatchlistItemDetailResponse,
)
from app.schemas.symbol import (
    SymbolResponse,
    TechnicalIndicatorResponse,
    MarketStateResponse,
)

router = APIRouter()


@router.get("/", response_model=List[WatchlistItemDetailResponse])
async def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    현재 사용자의 관심 종목 목록 조회

    각 종목의 최신 지표 및 시장 상태 정보를 포함합니다.
    """
    watchlist_items = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id)
        .order_by(Watchlist.added_at.desc())
        .all()
    )

    result = []
    for item in watchlist_items:
        symbol = db.query(Symbol).filter(Symbol.id == item.symbol_id).first()
        if not symbol:
            continue

        # 최신 기술적 지표 조회
        latest_indicator = (
            db.query(TechnicalIndicator)
            .filter(TechnicalIndicator.symbol_id == symbol.id)
            .order_by(TechnicalIndicator.date.desc())
            .first()
        )

        # 최신 시장 상태 조회
        latest_market_state = (
            db.query(MarketState)
            .filter(MarketState.symbol_id == symbol.id)
            .order_by(MarketState.date.desc())
            .first()
        )

        # 현재 가격 (latest_indicator의 close 가격 사용)
        current_price = None
        if latest_indicator:
            # TechnicalIndicator에는 close 가격이 없으므로, 별도로 조회하거나 생략
            # 여기서는 None으로 설정 (실제로는 FMP API에서 실시간 가격 조회 가능)
            current_price = None

        result.append(
            WatchlistItemDetailResponse(
                id=item.id,
                user_id=item.user_id,
                added_at=item.added_at,
                notes=item.notes,
                symbol=SymbolResponse(
                    id=symbol.id,
                    symbol=symbol.symbol,
                    name=symbol.name,
                    exchange=symbol.exchange,
                    last_updated=symbol.last_updated,
                ),
                current_price=current_price,
                latest_indicator=(
                    TechnicalIndicatorResponse(
                        date=latest_indicator.date,
                        atr=float(latest_indicator.atr) if latest_indicator.atr else None,
                        atr_ratio=float(latest_indicator.atr_ratio) if latest_indicator.atr_ratio else None,
                        bb_upper=float(latest_indicator.bb_upper) if latest_indicator.bb_upper else None,
                        bb_middle=float(latest_indicator.bb_middle) if latest_indicator.bb_middle else None,
                        bb_lower=float(latest_indicator.bb_lower) if latest_indicator.bb_lower else None,
                        bb_width_ratio=float(latest_indicator.bb_width_ratio) if latest_indicator.bb_width_ratio else None,
                        adx=float(latest_indicator.adx) if latest_indicator.adx else None,
                        plus_di=float(latest_indicator.plus_di) if latest_indicator.plus_di else None,
                        minus_di=float(latest_indicator.minus_di) if latest_indicator.minus_di else None,
                        std_dev=float(latest_indicator.std_dev) if latest_indicator.std_dev else None,
                        vix=float(latest_indicator.vix) if latest_indicator.vix else None,
                    )
                    if latest_indicator
                    else None
                ),
                latest_market_state=(
                    MarketStateResponse(
                        date=latest_market_state.date,
                        trend_type=latest_market_state.trend_type,
                        volatility_level=latest_market_state.volatility_level,
                        risk_level=latest_market_state.risk_level,
                        recommended_strategy=latest_market_state.recommended_strategy,
                        position_sizing_ratio=float(latest_market_state.position_sizing_ratio),
                    )
                    if latest_market_state
                    else None
                ),
            )
        )

    return result


@router.post("/", response_model=WatchlistItemResponse, status_code=201)
async def add_to_watchlist(
    watchlist_item: WatchlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    관심 종목 추가

    - **symbol_id**: 추가할 종목의 ID (Symbol 테이블의 ID)
    - **notes**: 메모 (선택사항)
    """
    # 종목 존재 여부 확인
    symbol = db.query(Symbol).filter(Symbol.id == watchlist_item.symbol_id).first()
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    # 이미 관심 종목에 있는지 확인
    existing = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == current_user.id,
            Watchlist.symbol_id == watchlist_item.symbol_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Symbol already in watchlist")

    # 새 관심 종목 추가
    new_item = Watchlist(
        user_id=current_user.id,
        symbol_id=watchlist_item.symbol_id,
        notes=watchlist_item.notes,
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return WatchlistItemResponse(
        id=new_item.id,
        user_id=new_item.user_id,
        symbol_id=new_item.symbol_id,
        notes=new_item.notes,
        added_at=new_item.added_at,
    )


@router.patch("/{watchlist_id}", response_model=WatchlistItemResponse)
async def update_watchlist_item(
    watchlist_id: int,
    update_data: WatchlistItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    관심 종목 메모 업데이트

    - **watchlist_id**: 관심 종목 ID
    - **notes**: 새로운 메모 내용
    """
    item = (
        db.query(Watchlist)
        .filter(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == current_user.id,
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    if update_data.notes is not None:
        item.notes = update_data.notes

    db.commit()
    db.refresh(item)

    return WatchlistItemResponse(
        id=item.id,
        user_id=item.user_id,
        symbol_id=item.symbol_id,
        notes=item.notes,
        added_at=item.added_at,
    )


@router.delete("/{watchlist_id}", status_code=204)
async def remove_from_watchlist(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    관심 종목 제거

    - **watchlist_id**: 제거할 관심 종목 ID
    """
    item = (
        db.query(Watchlist)
        .filter(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == current_user.id,
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    db.delete(item)
    db.commit()

    return None
