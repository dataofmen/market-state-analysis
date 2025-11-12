"""
Trading Signals API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from app.core import deps
from app.models import Symbol, FundamentalScore, TradingSignal
from app.services.fmp_client import fmp_client
from app.services.fundamental_analysis import fundamental_service
from app.services.indicators import TechnicalIndicators
from app.services.hybrid_signal import hybrid_signal_generator
from app.services.multi_timeframe import multi_timeframe_analyzer
import pandas as pd
import math

router = APIRouter()


def _safe_float(value) -> float | None:
    """pandas/numpy float을 Python float으로 안전하게 변환 (NaN/Inf는 None으로)"""
    if pd.isna(value):
        return None
    try:
        val = float(value)
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    except (TypeError, ValueError):
        return None


@router.get("/{symbol}")
async def get_trading_signal(
    symbol: str,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    """
    종목의 최신 매매 시그널 조회 (또는 생성)

    하이브리드 매매 시그널:
    - Piotroski F-Score (재무 건전성)
    - 기술적 지표 (RSI, ADX, 이동평균선, 볼륨)
    - Golden/Death Cross
    - 매매 추천 및 리스크 평가
    """

    # 1. 심볼 조회 또는 생성
    symbol_upper = symbol.upper()
    db_symbol = db.query(Symbol).filter(Symbol.symbol == symbol_upper).first()

    if not db_symbol:
        # 새로운 심볼 생성
        symbol_info = await fmp_client.get_company_profile(symbol_upper)
        if not symbol_info:
            raise HTTPException(status_code=404, detail="Symbol not found")

        db_symbol = Symbol(
            symbol=symbol_upper,
            name=symbol_info.get("name", symbol_upper),
            exchange=symbol_info.get("exchange", "Unknown"),
        )
        db.add(db_symbol)
        db.commit()
        db.refresh(db_symbol)

    # 2. 최신 F-Score 확인 (24시간 이내)
    recent_f_score = (
        db.query(FundamentalScore)
        .filter(FundamentalScore.symbol_id == db_symbol.id)
        .filter(FundamentalScore.calculated_at >= datetime.utcnow() - timedelta(hours=24))
        .order_by(FundamentalScore.calculated_at.desc())
        .first()
    )

    if not recent_f_score:
        # F-Score 계산
        f_score_data = await fundamental_service.get_f_score(symbol_upper)

        # DB에 저장
        fundamentals = f_score_data.get("fundamentals", {})
        db_f_score = FundamentalScore(
            symbol_id=db_symbol.id,
            f_score=f_score_data.get("f_score", 0),
            max_score=f_score_data.get("max_score", 9),
            score_details=f_score_data.get("details", {}),
            market_cap=fundamentals.get("market_cap"),
            pe_ratio=fundamentals.get("pe_ratio"),
            pb_ratio=fundamentals.get("pb_ratio"),
            debt_to_equity=fundamentals.get("debt_to_equity"),
            current_ratio=fundamentals.get("current_ratio"),
            roe=fundamentals.get("roe"),
            roa=fundamentals.get("roa"),
            profit_margin=fundamentals.get("profit_margin"),
            operating_margin=fundamentals.get("operating_margin"),
            gross_margin=fundamentals.get("gross_margin"),
        )
        db.add(db_f_score)
        db.commit()
        db.refresh(db_f_score)
    else:
        db_f_score = recent_f_score
        f_score_data = {
            "f_score": db_f_score.f_score,
            "max_score": db_f_score.max_score,
            "details": db_f_score.score_details,
        }

    # 3. 최신 가격 데이터 조회 (200일치 - 이동평균선 계산용)
    price_data = await fmp_client.get_historical_prices(
        symbol=symbol_upper, from_date=None, to_date=None
    )

    if not price_data or len(price_data) < 50:
        raise HTTPException(
            status_code=400,
            detail="Insufficient price data for signal generation (need at least 50 days)",
        )

    # 4. 기술적 지표 계산
    df = TechnicalIndicators.calculate_all_indicators(price_data)

    # 5. 다중 타임프레임 분석 수행
    timeframe_analysis = await multi_timeframe_analyzer.analyze_multiple_timeframes(
        symbol=symbol_upper, trading_style="swing_trading"
    )

    # 진입점 최적화 분석 추가
    timeframe_analysis["entry_analysis"] = multi_timeframe_analyzer.get_optimal_entry_analysis(
        timeframe_analysis
    )

    # 6. 하이브리드 시그널 생성 (타임프레임 분석 포함)
    current_price = _safe_float(df.iloc[-1]["close"]) or 0.0
    signal_data = hybrid_signal_generator.generate_signal(
        f_score_data=f_score_data,
        technical_data=df,
        current_price=current_price,
        timeframe_analysis=timeframe_analysis,
    )

    # 7. 시그널 DB 저장 (타임프레임 분석 포함)
    db_signal = TradingSignal(
        symbol_id=db_symbol.id,
        fundamental_score_id=db_f_score.id,
        signal_type=signal_data["signal_type"],
        signal_strength=signal_data["signal_strength"],
        current_price=signal_data["current_price"],
        conditions=signal_data["conditions"],
        recommendations=signal_data["recommendations"],
        risk_level=signal_data["risk_assessment"]["risk_level"],
        risk_factors=signal_data["risk_assessment"]["risk_factors"],
        timeframe_analysis=timeframe_analysis,  # 타임프레임 분석 결과 저장
    )
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)

    # 8. 응답 데이터 구성 (타임프레임 분석 포함)
    return {
        "symbol": {
            "symbol": db_symbol.symbol,
            "name": db_symbol.name,
            "exchange": db_symbol.exchange,
        },
        "signal": {
            "id": db_signal.id,
            "signal_type": db_signal.signal_type,
            "signal_strength": db_signal.signal_strength,
            "current_price": db_signal.current_price,
            "generated_at": db_signal.generated_at.isoformat(),
        },
        "f_score": {
            "score": db_f_score.f_score,
            "max_score": db_f_score.max_score,
            "details": db_f_score.score_details,
            "calculated_at": db_f_score.calculated_at.isoformat(),
        },
        "timeframe_analysis": timeframe_analysis,  # 다중 타임프레임 분석 결과
        "conditions": signal_data["conditions"],
        "recommendations": signal_data["recommendations"],
        "risk_assessment": signal_data["risk_assessment"],
        "technical_indicators": {
            "rsi": _safe_float(df.iloc[-1]["rsi"]) if "rsi" in df.columns else None,
            "adx": _safe_float(df.iloc[-1]["adx"]) if "adx" in df.columns else None,
            "sma_50": _safe_float(df.iloc[-1]["sma_50"]) if "sma_50" in df.columns else None,
            "sma_200": _safe_float(df.iloc[-1]["sma_200"])
            if "sma_200" in df.columns
            else None,
        },
    }


@router.get("/{symbol}/history")
async def get_signal_history(
    symbol: str,
    limit: int = 30,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    """
    종목의 과거 시그널 이력 조회

    Args:
        symbol: 종목 코드
        limit: 조회할 최대 개수 (기본값: 30)
    """

    symbol_upper = symbol.upper()
    db_symbol = db.query(Symbol).filter(Symbol.symbol == symbol_upper).first()

    if not db_symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    # 시그널 이력 조회
    signals = (
        db.query(TradingSignal)
        .filter(TradingSignal.symbol_id == db_symbol.id)
        .order_by(TradingSignal.generated_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "symbol": {
            "symbol": db_symbol.symbol,
            "name": db_symbol.name,
        },
        "total_count": len(signals),
        "signals": [
            {
                "id": signal.id,
                "signal_type": signal.signal_type,
                "signal_strength": signal.signal_strength,
                "current_price": signal.current_price,
                "risk_level": signal.risk_level,
                "generated_at": signal.generated_at.isoformat(),
            }
            for signal in signals
        ],
    }


@router.get("/")
async def get_all_signals(
    signal_type: str = None,
    limit: int = 50,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    """
    전체 종목의 최신 시그널 조회

    Args:
        signal_type: 시그널 타입 필터 (strong_buy, buy, hold, warning, sell, strong_sell)
        limit: 조회할 최대 개수 (기본값: 50)
    """

    # 각 심볼별 최신 시그널만 조회
    subquery = (
        db.query(
            TradingSignal.symbol_id,
            func.max(TradingSignal.generated_at).label("max_date"),
        )
        .group_by(TradingSignal.symbol_id)
        .subquery()
    )

    query = (
        db.query(TradingSignal, Symbol)
        .join(subquery, TradingSignal.symbol_id == subquery.c.symbol_id)
        .filter(TradingSignal.generated_at == subquery.c.max_date)
        .join(Symbol, TradingSignal.symbol_id == Symbol.id)
    )

    if signal_type:
        query = query.filter(TradingSignal.signal_type == signal_type)

    signals = query.order_by(TradingSignal.generated_at.desc()).limit(limit).all()

    return {
        "total_count": len(signals),
        "signals": [
            {
                "symbol": {
                    "symbol": symbol.symbol,
                    "name": symbol.name,
                },
                "signal": {
                    "id": signal.id,
                    "signal_type": signal.signal_type,
                    "signal_strength": signal.signal_strength,
                    "current_price": signal.current_price,
                    "risk_level": signal.risk_level,
                    "generated_at": signal.generated_at.isoformat(),
                },
            }
            for signal, symbol in signals
        ],
    }
