from celery import Task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List
import asyncio

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.symbol import Symbol
from app.models.watchlist import Watchlist
from app.models.technical_indicator import TechnicalIndicator
from app.models.market_state import MarketState
from app.models.data_update_log import DataUpdateLog
from app.services.fmp_client import fmp_client
from app.services.indicators import TechnicalIndicators
from app.services.market_classifier import MarketClassifier


class DatabaseTask(Task):
    """데이터베이스 세션을 자동으로 관리하는 Celery Task"""

    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.data_update.update_symbol_data")
def update_symbol_data(self, symbol_id: int) -> dict:
    """
    단일 종목의 기술적 지표 및 시장 상태 업데이트

    Args:
        symbol_id: Symbol 테이블의 ID

    Returns:
        업데이트 결과 딕셔너리
    """
    db = self.db

    try:
        # 1. Symbol 조회
        symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
        if not symbol:
            return {"status": "error", "message": f"Symbol {symbol_id} not found"}

        # 2. FMP API에서 최근 90일 가격 데이터 가져오기
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        # asyncio.run()으로 비동기 함수 호출
        price_data = asyncio.run(
            fmp_client.get_historical_prices(
                symbol=symbol.symbol,
                from_date=from_date,
                to_date=to_date
            )
        )

        if not price_data or len(price_data) < 30:
            return {
                "status": "error",
                "message": f"Insufficient price data for {symbol.symbol}"
            }

        # 3. 기술적 지표 계산
        indicators_df = TechnicalIndicators.calculate_all_indicators(price_data)

        # 4. VIX 가져오기
        vix_value = asyncio.run(fmp_client.get_vix())

        # 5. 최신 데이터 저장
        latest_row = indicators_df.iloc[-1]
        latest_date = latest_row["date"].date()

        # TechnicalIndicator 저장/업데이트
        existing_indicator = (
            db.query(TechnicalIndicator)
            .filter(
                TechnicalIndicator.symbol_id == symbol.id,
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
        else:
            # 새로 생성
            db_indicator = TechnicalIndicator(
                symbol_id=symbol.id,
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

        # MarketState 저장/업데이트
        existing_state = (
            db.query(MarketState)
            .filter(
                MarketState.symbol_id == symbol.id,
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
        else:
            # 새로 생성
            db_state = MarketState(
                symbol_id=symbol.id,
                date=latest_date,
                trend_type=classification["trend_type"],
                volatility_level=classification["volatility_level"],
                risk_level=classification["risk_level"],
                recommended_strategy=classification["recommended_strategy"],
                position_sizing_ratio=Decimal(str(classification["position_sizing_ratio"])),
            )
            db.add(db_state)

        # 7. Symbol의 last_updated 업데이트
        symbol.last_updated = datetime.now()
        db.commit()

        return {
            "status": "success",
            "symbol": symbol.symbol,
            "updated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "symbol_id": symbol_id,
            "message": str(e),
        }


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.data_update.update_all_watchlist_symbols")
def update_all_watchlist_symbols(self) -> dict:
    """
    모든 사용자의 관심 종목 데이터 업데이트

    Returns:
        업데이트 결과 딕셔너리
    """
    db = self.db

    try:
        # 로그 생성
        log = DataUpdateLog(
            update_type="watchlist_symbols",
            status="running",
            started_at=datetime.now(),
        )
        db.add(log)
        db.commit()

        # 관심 종목에 있는 모든 심볼 ID 조회 (중복 제거)
        symbol_ids = (
            db.query(Watchlist.symbol_id)
            .distinct()
            .all()
        )

        symbol_ids = [sid[0] for sid in symbol_ids]

        # 각 심볼별 업데이트 태스크 실행
        results = []
        for symbol_id in symbol_ids:
            result = update_symbol_data(symbol_id)
            results.append(result)

        # 성공/실패 카운트
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = sum(1 for r in results if r.get("status") == "error")

        # 로그 업데이트
        log.status = "completed" if error_count == 0 else "partial_success"
        log.completed_at = datetime.now()
        log.records_processed = len(symbol_ids)
        log.records_success = success_count
        log.records_failed = error_count

        if error_count > 0:
            error_details = [r for r in results if r.get("status") == "error"]
            log.error_message = f"Failed symbols: {error_details}"

        db.commit()

        return {
            "status": "completed",
            "total": len(symbol_ids),
            "success": success_count,
            "failed": error_count,
            "results": results,
        }

    except Exception as e:
        db.rollback()
        # 로그 업데이트
        if log:
            log.status = "failed"
            log.completed_at = datetime.now()
            log.error_message = str(e)
            db.commit()

        return {
            "status": "error",
            "message": str(e),
        }


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.data_update.cleanup_old_data")
def cleanup_old_data(self, days: int = 365) -> dict:
    """
    오래된 데이터 정리 (1년 이상)

    Args:
        days: 유지할 일수 (기본값: 365일)

    Returns:
        정리 결과 딕셔너리
    """
    db = self.db

    try:
        cutoff_date = date.today() - timedelta(days=days)

        # TechnicalIndicator 정리
        deleted_indicators = (
            db.query(TechnicalIndicator)
            .filter(TechnicalIndicator.date < cutoff_date)
            .delete(synchronize_session=False)
        )

        # MarketState 정리
        deleted_states = (
            db.query(MarketState)
            .filter(MarketState.date < cutoff_date)
            .delete(synchronize_session=False)
        )

        # DataUpdateLog 정리 (90일 이상)
        log_cutoff_date = datetime.now() - timedelta(days=90)
        deleted_logs = (
            db.query(DataUpdateLog)
            .filter(DataUpdateLog.started_at < log_cutoff_date)
            .delete(synchronize_session=False)
        )

        db.commit()

        return {
            "status": "success",
            "deleted_indicators": deleted_indicators,
            "deleted_market_states": deleted_states,
            "deleted_logs": deleted_logs,
            "cutoff_date": cutoff_date.isoformat(),
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e),
        }
