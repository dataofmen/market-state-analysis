"""
Multi-Timeframe Analysis Service
다중 타임프레임 분석 - 트레이딩 성공의 핵심 요소
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.services.fmp_client import fmp_client
from app.services.indicators import TechnicalIndicators


class TimeFrame(str, Enum):
    """타임프레임 정의"""
    MINUTE_1 = "1min"
    MINUTE_5 = "5min"
    MINUTE_15 = "15min"
    MINUTE_30 = "30min"
    HOUR_1 = "1hour"
    HOUR_4 = "4hour"
    DAILY = "1day"
    WEEKLY = "1week"


class TrendDirection(str, Enum):
    """추세 방향"""
    BULLISH = "bullish"  # 상승
    BEARISH = "bearish"  # 하락
    SIDEWAYS = "sideways"  # 횡보


class AlignmentStatus(str, Enum):
    """타임프레임 정렬 상태"""
    ALIGNED = "aligned"  # 완전 정렬 - 모든 타임프레임이 같은 방향
    PARTIAL_ALIGNED = "partial_aligned"  # 부분 정렬 - 일부만 정렬
    CONFLICTED = "conflicted"  # 충돌 - 타임프레임들이 다른 방향


class MultiTimeframeAnalyzer:
    """
    다중 타임프레임 분석기

    핵심 원칙:
    1. 상위 타임프레임이 하위 타임프레임보다 중요
    2. 완전 정렬 시 고확률 설정 (80%의 거래는 정렬된 상태에서)
    3. 충돌 시에는 거래 회피
    4. 부분 정렬 시 선택적 진입
    """

    # 트레이딩 스타일별 권장 타임프레임
    TRADING_STYLE_TIMEFRAMES = {
        "day_trading": {
            "primary": [TimeFrame.DAILY, TimeFrame.HOUR_1],
            "entry_early": [TimeFrame.MINUTE_1, TimeFrame.MINUTE_5],
            "entry_later": [TimeFrame.MINUTE_5, TimeFrame.MINUTE_15],
        },
        "swing_trading": {
            "primary": [TimeFrame.WEEKLY, TimeFrame.DAILY, TimeFrame.HOUR_1],
            "entry": [TimeFrame.HOUR_1, TimeFrame.DAILY],
        },
        "vwap_strategy": {
            "primary": [TimeFrame.HOUR_1, TimeFrame.HOUR_4],
            "entry": [TimeFrame.MINUTE_15, TimeFrame.MINUTE_30],
        },
    }

    def __init__(self):
        pass

    def _determine_trend(self, df: pd.DataFrame) -> TrendDirection:
        """
        타임프레임의 추세 방향 판단

        기준:
        - 이동평균선 정배열/역배열
        - 가격이 이동평균선 위/아래
        - ADX 강도
        """
        if len(df) < 50:
            return TrendDirection.SIDEWAYS

        latest = df.iloc[-1]

        # 이동평균선 확인
        sma_20 = latest.get("sma_20")
        sma_50 = latest.get("sma_50")
        close = latest.get("close")
        adx = latest.get("adx", 0)

        # NaN 체크
        if pd.isna([sma_20, sma_50, close]).any():
            return TrendDirection.SIDEWAYS

        # 추세 강도 확인 (ADX)
        weak_trend = adx < 25

        # 상승 추세 조건
        if sma_20 > sma_50 and close > sma_20:
            if weak_trend:
                return TrendDirection.SIDEWAYS
            return TrendDirection.BULLISH

        # 하락 추세 조건
        if sma_20 < sma_50 and close < sma_20:
            if weak_trend:
                return TrendDirection.SIDEWAYS
            return TrendDirection.BEARISH

        return TrendDirection.SIDEWAYS

    async def _get_timeframe_data(
        self, symbol: str, days: int
    ) -> pd.DataFrame:
        """특정 일수의 가격 데이터 조회 및 지표 계산"""
        try:
            price_data = await fmp_client.get_historical_prices(
                symbol=symbol, from_date=None, to_date=None
            )

            # 요청한 일수만큼만 가져오기
            if len(price_data) > days:
                price_data = price_data[-days:]

            # 기술적 지표 계산
            df = TechnicalIndicators.calculate_all_indicators(price_data)
            return df
        except Exception as e:
            print(f"Error fetching timeframe data for {symbol}: {e}")
            return pd.DataFrame()

    async def analyze_multiple_timeframes(
        self,
        symbol: str,
        trading_style: str = "swing_trading",
    ) -> Dict[str, Any]:
        """
        다중 타임프레임 분석 수행

        Args:
            symbol: 종목 심볼
            trading_style: 트레이딩 스타일 (day_trading, swing_trading, vwap_strategy)

        Returns:
            타임프레임별 추세, 정렬 상태, 진입 적합성 등
        """

        # 타임프레임별 데이터 수집 (일수 기준)
        timeframe_configs = {
            "short_term": {"days": 20, "label": "단기 (20일)"},  # 하위
            "medium_term": {"days": 100, "label": "중기 (100일)"},  # 현재
            "long_term": {"days": 200, "label": "장기 (200일)"},  # 상위
        }

        results = {}
        trends = []

        # 각 타임프레임별 분석
        for tf_key, config in timeframe_configs.items():
            df = await self._get_timeframe_data(symbol, config["days"])

            if df.empty or len(df) < 20:
                results[tf_key] = {
                    "label": config["label"],
                    "trend": TrendDirection.SIDEWAYS,
                    "data_available": False,
                }
                trends.append(TrendDirection.SIDEWAYS)
                continue

            trend = self._determine_trend(df)
            latest = df.iloc[-1]

            results[tf_key] = {
                "label": config["label"],
                "trend": trend,
                "data_available": True,
                "indicators": {
                    "sma_20": float(latest.get("sma_20", 0)) if not pd.isna(latest.get("sma_20")) else None,
                    "sma_50": float(latest.get("sma_50", 0)) if not pd.isna(latest.get("sma_50")) else None,
                    "adx": float(latest.get("adx", 0)) if not pd.isna(latest.get("adx")) else None,
                    "rsi": float(latest.get("rsi", 0)) if not pd.isna(latest.get("rsi")) else None,
                },
            }
            trends.append(trend)

        # 정렬 상태 판단
        alignment_status = self._determine_alignment(trends)

        # 거래 적합성 평가
        trade_suitability = self._evaluate_trade_suitability(
            alignment_status, results, trading_style
        )

        return {
            "timeframes": results,
            "alignment_status": alignment_status,
            "trade_suitability": trade_suitability,
            "analyzed_at": datetime.now().isoformat(),
        }

    def _determine_alignment(self, trends: List[TrendDirection]) -> AlignmentStatus:
        """
        타임프레임 정렬 상태 판단

        완전 정렬: 모든 타임프레임이 같은 방향
        부분 정렬: 일부만 같은 방향
        충돌: 타임프레임들이 명확히 다른 방향
        """
        if not trends:
            return AlignmentStatus.CONFLICTED

        # 횡보 제외
        non_sideways = [t for t in trends if t != TrendDirection.SIDEWAYS]

        if len(non_sideways) == 0:
            return AlignmentStatus.CONFLICTED

        # 모두 같은 방향
        if len(set(non_sideways)) == 1:
            return AlignmentStatus.ALIGNED

        # 상위 타임프레임(장기) 추세 확인
        long_term_trend = trends[-1] if len(trends) >= 3 else trends[0]

        # 상위 타임프레임과 일치하는 추세 개수
        matching = sum(1 for t in non_sideways if t == long_term_trend)

        # 과반 이상 일치하면 부분 정렬
        if matching >= len(non_sideways) / 2:
            return AlignmentStatus.PARTIAL_ALIGNED

        return AlignmentStatus.CONFLICTED

    def _evaluate_trade_suitability(
        self,
        alignment_status: AlignmentStatus,
        timeframe_results: Dict[str, Any],
        trading_style: str,
    ) -> Dict[str, Any]:
        """
        거래 적합성 평가

        Returns:
            should_trade: 거래 가능 여부
            confidence: 신뢰도 (0-100)
            recommendation: 권장사항
            warnings: 경고사항
        """

        # 기본값
        should_trade = False
        confidence = 0
        recommendations = []
        warnings = []

        # 장기(상위) 타임프레임 추세
        long_term = timeframe_results.get("long_term", {})
        long_trend = long_term.get("trend", TrendDirection.SIDEWAYS)

        # 중기(현재) 타임프레임 추세
        medium_term = timeframe_results.get("medium_term", {})
        medium_trend = medium_term.get("trend", TrendDirection.SIDEWAYS)

        # 단기(하위) 타임프레임 추세
        short_term = timeframe_results.get("short_term", {})
        short_trend = short_term.get("trend", TrendDirection.SIDEWAYS)

        # === 완전 정렬 (최고 품질) ===
        if alignment_status == AlignmentStatus.ALIGNED:
            should_trade = True
            confidence = 90

            if long_trend == TrendDirection.BULLISH:
                recommendations.append("✅ 완전 정렬 (모든 타임프레임 상승)")
                recommendations.append("💪 강력한 매수 신호")
                recommendations.append("🎯 이상적인 진입 기회")
            elif long_trend == TrendDirection.BEARISH:
                recommendations.append("✅ 완전 정렬 (모든 타임프레임 하락)")
                recommendations.append("🔻 강력한 매도 신호")
                recommendations.append("⚠️ 매수 포지션 청산 권장")

        # === 부분 정렬 (선택적 진입) ===
        elif alignment_status == AlignmentStatus.PARTIAL_ALIGNED:
            # 상위 타임프레임이 우호적인지 확인
            if long_trend != TrendDirection.SIDEWAYS:
                should_trade = True
                confidence = 65

                recommendations.append("🟡 부분 정렬 - 선택적 진입 가능")

                # 하위 타임프레임과 불일치 시
                if short_trend != long_trend and short_trend != TrendDirection.SIDEWAYS:
                    recommendations.append("⏳ 하위 타임프레임 전환 대기 권장")
                    recommendations.append("📊 진입 시점 최적화 가능")
                    confidence = 55
                else:
                    recommendations.append("✓ 장기 편향 유리")

                if long_trend == TrendDirection.BULLISH:
                    recommendations.append("↗️ 상위 타임프레임 상승세")
                elif long_trend == TrendDirection.BEARISH:
                    recommendations.append("↘️ 상위 타임프레임 하락세")
            else:
                warnings.append("⚠️ 상위 타임프레임 방향성 불분명")
                confidence = 30

        # === 충돌 (거래 회피) ===
        else:
            should_trade = False
            confidence = 20
            warnings.append("🚫 타임프레임 충돌 - 거래 회피")
            warnings.append("⏸️ 명확한 방향성 확립 대기")

            # 구체적인 충돌 상황 설명
            if long_trend == TrendDirection.BULLISH and short_trend == TrendDirection.BEARISH:
                warnings.append("📉 상위 타임프레임 상승 vs 하위 타임프레임 하락")
            elif long_trend == TrendDirection.BEARISH and short_trend == TrendDirection.BULLISH:
                warnings.append("📈 상위 타임프레임 하락 vs 하위 타임프레임 상승")

        # 횡보 경고
        if long_trend == TrendDirection.SIDEWAYS:
            warnings.append("⚡ 상위 타임프레임 횡보 - 방향성 불분명")

        return {
            "should_trade": should_trade,
            "confidence": confidence,
            "recommendations": recommendations,
            "warnings": warnings,
            "primary_timeframe_trend": long_trend,
            "entry_timeframe_trend": short_trend,
        }

    def get_optimal_entry_analysis(
        self,
        timeframe_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        최적 진입점 분석

        상위 타임프레임에서 설정 발견 → 하위 타임프레임에서 진입점 찾기
        - 더 나은 진입가
        - 더 타이트한 손절가
        - 더 나은 위험 대비 보상 비율
        """

        suitability = timeframe_analysis.get("trade_suitability", {})
        should_trade = suitability.get("should_trade", False)

        if not should_trade:
            return {
                "entry_recommended": False,
                "reason": "타임프레임 정렬 불충분",
            }

        primary_trend = suitability.get("primary_timeframe_trend")
        entry_trend = suitability.get("entry_timeframe_trend")

        entry_strategy = []

        # 상위와 하위 타임프레임이 일치하는 경우
        if primary_trend == entry_trend:
            entry_strategy.append("✅ 즉시 진입 가능 - 모든 타임프레임 정렬")
            entry_strategy.append("🎯 현재 가격에서 진입 고려")
        else:
            entry_strategy.append("⏳ 하위 타임프레임 전환 대기")
            entry_strategy.append("📊 더 나은 진입가 포착 가능")

            if primary_trend == TrendDirection.BULLISH:
                entry_strategy.append("💡 단기 조정 후 매수 진입")
            elif primary_trend == TrendDirection.BEARISH:
                entry_strategy.append("💡 단기 반등 후 매도 진입")

        return {
            "entry_recommended": True,
            "primary_trend": primary_trend,
            "entry_trend": entry_trend,
            "entry_strategy": entry_strategy,
            "stop_loss_optimization": "하위 타임프레임 스윙 포인트 활용 가능",
        }


# 싱글톤 인스턴스
multi_timeframe_analyzer = MultiTimeframeAnalyzer()
