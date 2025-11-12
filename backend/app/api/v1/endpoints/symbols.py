from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.symbol import Symbol
from app.models.technical_indicator import TechnicalIndicator
from app.models.market_state import MarketState
from app.schemas.symbol import (
    SymbolResponse,
    SymbolDetailResponse,
    SymbolSearchResponse,
    TechnicalIndicatorResponse,
    MarketStateResponse,
)
from app.services.fmp_client import fmp_client
from app.services.indicators import TechnicalIndicators
from app.services.market_classifier import MarketClassifier
from decimal import Decimal

router = APIRouter()


@router.get("/search", response_model=List[SymbolSearchResponse])
async def search_symbols(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """
    종목 검색 (FMP API)

    - **query**: 검색어 (심볼 또는 회사명)
    - **limit**: 결과 개수 제한 (기본값: 10)
    """
    try:
        results = await fmp_client.search_symbols(query, limit=limit)
        return [
            SymbolSearchResponse(
                symbol=item.get("symbol", ""),
                name=item.get("name", ""),
                exchange=item.get("stockExchange", ""),
                currency=item.get("currency"),
                stock_type=item.get("exchangeShortName"),
            )
            for item in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search symbols: {str(e)}")


@router.get("/{symbol}", response_model=SymbolDetailResponse)
async def get_symbol_detail(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    종목 상세 정보 조회 (지표 + 시장 상태 분석 포함)

    - **symbol**: 종목 심볼 (예: AAPL, MSFT)

    자동으로 FMP API에서 데이터를 가져와 분석하고 DB에 저장합니다.
    """
    symbol = symbol.upper()

    try:
        # 1. Symbol 정보 가져오기 또는 생성
        db_symbol = db.query(Symbol).filter(Symbol.symbol == symbol).first()

        if not db_symbol:
            # FMP에서 회사 프로필 가져오기
            profile = await fmp_client.get_company_profile(symbol)
            if not profile:
                raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

            db_symbol = Symbol(
                symbol=symbol,
                name=profile.get("companyName", symbol),
                exchange=profile.get("exchangeShortName", ""),
            )
            db.add(db_symbol)
            db.commit()
            db.refresh(db_symbol)

        # 2. 최근 90일 가격 데이터 가져오기
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        price_data = await fmp_client.get_historical_prices(
            symbol=symbol,
            from_date=from_date,
            to_date=to_date
        )

        if not price_data or len(price_data) < 30:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient price data for {symbol}"
            )

        # 3. 기술적 지표 계산
        indicators_df = TechnicalIndicators.calculate_all_indicators(price_data)

        # 4. VIX 가져오기 (S&P 500 지수 종목인 경우)
        vix_value = await fmp_client.get_vix()

        # 5. 최신 데이터 저장 및 시장 상태 분류
        latest_row = indicators_df.iloc[-1]
        latest_date = latest_row["date"].date()

        # TechnicalIndicator 저장
        existing_indicator = (
            db.query(TechnicalIndicator)
            .filter(
                TechnicalIndicator.symbol_id == db_symbol.id,
                TechnicalIndicator.date == latest_date,
            )
            .first()
        )

        if existing_indicator:
            # 업데이트
            for key in ["atr", "atr_ratio", "bb_upper", "bb_middle", "bb_lower",
                       "bb_width", "bb_width_ratio", "adx", "plus_di", "minus_di", "std_dev"]:
                if key in latest_row and not latest_row.isna()[key]:
                    setattr(existing_indicator, key, Decimal(str(latest_row[key])))
            existing_indicator.vix = Decimal(str(vix_value))
            db_indicator = existing_indicator
        else:
            # 새로 생성
            db_indicator = TechnicalIndicator(
                symbol_id=db_symbol.id,
                date=latest_date,
                atr=Decimal(str(latest_row["atr"])),
                atr_ratio=Decimal(str(latest_row["atr_ratio"])),
                bb_upper=Decimal(str(latest_row["bb_upper"])),
                bb_middle=Decimal(str(latest_row["bb_middle"])),
                bb_lower=Decimal(str(latest_row["bb_lower"])),
                bb_width=Decimal(str(latest_row["bb_width"])),
                bb_width_ratio=Decimal(str(latest_row["bb_width_ratio"])),
                adx=Decimal(str(latest_row["adx"])),
                plus_di=Decimal(str(latest_row["plus_di"])),
                minus_di=Decimal(str(latest_row["minus_di"])),
                std_dev=Decimal(str(latest_row["std_dev"])),
                vix=Decimal(str(vix_value)),
            )
            db.add(db_indicator)

        db.commit()
        db.refresh(db_indicator)

        # 6. 시장 상태 분류
        indicators_dict = {
            "adx": float(latest_row["adx"]),
            "plus_di": float(latest_row["plus_di"]),
            "minus_di": float(latest_row["minus_di"]),
            "atr_ratio": float(latest_row["atr_ratio"]),
            "bb_width_ratio": float(latest_row["bb_width_ratio"]),
            "std_dev": float(latest_row["std_dev"]),
            "close": float(latest_row["close"]),
            "vix": vix_value,
        }

        classification = MarketClassifier.classify_market_state(indicators_dict)

        # MarketState 저장
        existing_state = (
            db.query(MarketState)
            .filter(
                MarketState.symbol_id == db_symbol.id,
                MarketState.date == latest_date,
            )
            .first()
        )

        if existing_state:
            # 업데이트
            existing_state.trend_type = classification["trend_type"]
            existing_state.volatility_level = classification["volatility_level"]
            existing_state.risk_level = classification["risk_level"]
            existing_state.recommended_strategy = classification["recommended_strategy"]
            existing_state.position_sizing_ratio = Decimal(str(classification["position_sizing_ratio"]))
            db_state = existing_state
        else:
            # 새로 생성
            db_state = MarketState(
                symbol_id=db_symbol.id,
                date=latest_date,
                trend_type=classification["trend_type"],
                volatility_level=classification["volatility_level"],
                risk_level=classification["risk_level"],
                recommended_strategy=classification["recommended_strategy"],
                position_sizing_ratio=Decimal(str(classification["position_sizing_ratio"])),
            )
            db.add(db_state)

        db.commit()
        db.refresh(db_state)

        # 7. Symbol의 last_updated 업데이트
        db_symbol.last_updated = datetime.now()
        db.commit()

        # 8. 응답 생성
        return SymbolDetailResponse(
            symbol=SymbolResponse(
                id=db_symbol.id,
                symbol=db_symbol.symbol,
                name=db_symbol.name,
                exchange=db_symbol.exchange,
                last_updated=db_symbol.last_updated,
            ),
            current_price=float(latest_row["close"]),
            latest_indicator=TechnicalIndicatorResponse(
                date=db_indicator.date,
                atr=float(db_indicator.atr) if db_indicator.atr else None,
                atr_ratio=float(db_indicator.atr_ratio) if db_indicator.atr_ratio else None,
                bb_upper=float(db_indicator.bb_upper) if db_indicator.bb_upper else None,
                bb_middle=float(db_indicator.bb_middle) if db_indicator.bb_middle else None,
                bb_lower=float(db_indicator.bb_lower) if db_indicator.bb_lower else None,
                bb_width_ratio=float(db_indicator.bb_width_ratio) if db_indicator.bb_width_ratio else None,
                adx=float(db_indicator.adx) if db_indicator.adx else None,
                plus_di=float(db_indicator.plus_di) if db_indicator.plus_di else None,
                minus_di=float(db_indicator.minus_di) if db_indicator.minus_di else None,
                std_dev=float(db_indicator.std_dev) if db_indicator.std_dev else None,
                vix=float(db_indicator.vix) if db_indicator.vix else None,
            ),
            latest_market_state=MarketStateResponse(
                date=db_state.date,
                trend_type=db_state.trend_type,
                volatility_level=db_state.volatility_level,
                risk_level=db_state.risk_level,
                recommended_strategy=db_state.recommended_strategy,
                position_sizing_ratio=float(db_state.position_sizing_ratio),
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to get symbol detail: {str(e)}")


@router.get("/", response_model=List[SymbolResponse])
async def list_symbols(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    저장된 종목 목록 조회

    - **skip**: 건너뛸 개수 (페이징)
    - **limit**: 조회할 개수 (기본값: 20, 최대: 100)
    """
    symbols = (
        db.query(Symbol)
        .order_by(Symbol.last_updated.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        SymbolResponse(
            id=s.id,
            symbol=s.symbol,
            name=s.name,
            exchange=s.exchange,
            last_updated=s.last_updated,
        )
        for s in symbols
    ]
