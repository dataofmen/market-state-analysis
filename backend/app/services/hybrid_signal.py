"""
Hybrid Signal Generator - Piotroski F-Score + Technical Analysis

기본적 분석(F-Score)과 기술적 분석을 결합하여 매매 시그널을 생성합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class SignalType(str, Enum):
    """시그널 타입"""

    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    WARNING = "warning"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class SignalStrength(str, Enum):
    """시그널 강도"""

    VERY_STRONG = "very_strong"  # 5개 이상 조건 충족
    STRONG = "strong"  # 4개 조건 충족
    MODERATE = "moderate"  # 3개 조건 충족
    WEAK = "weak"  # 2개 이하 조건 충족


class HybridSignalGenerator:
    """하이브리드 매매 시그널 생성기"""

    @staticmethod
    def _convert_to_native_types(obj: Any) -> Any:
        """numpy/pandas 타입을 Python 기본 타입으로 변환"""
        if isinstance(obj, (np.integer, np.floating)):
            val = obj.item()
            # NaN/Inf 처리
            if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
                return None
            return val
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: HybridSignalGenerator._convert_to_native_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [HybridSignalGenerator._convert_to_native_types(item) for item in obj]
        elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            # 일반 float NaN/Inf 처리
            return None
        return obj

    def generate_signal(
        self,
        f_score_data: Dict[str, Any],
        technical_data: pd.DataFrame,
        current_price: float,
        timeframe_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        종합 매매 시그널 생성

        Args:
            f_score_data: Piotroski F-Score 데이터
            technical_data: 기술적 지표 데이터프레임
            current_price: 현재 가격
            timeframe_analysis: 다중 타임프레임 분석 결과 (선택)

        Returns:
            시그널 정보 딕셔너리
        """
        f_score = f_score_data.get("f_score", 0)
        latest_row = technical_data.iloc[-1]

        # === 시그널 조건 체크 ===
        conditions = self._check_conditions(f_score, latest_row, technical_data)

        # === 타임프레임 분석 통합 ===
        if timeframe_analysis:
            conditions = self._integrate_timeframe_analysis(conditions, timeframe_analysis)

        # === 시그널 타입 결정 ===
        signal_type = self._determine_signal_type(conditions, f_score, timeframe_analysis)

        # === 시그널 강도 계산 ===
        signal_strength = self._calculate_signal_strength(conditions, timeframe_analysis)

        # === 추천 액션 생성 ===
        recommendations = self._generate_recommendations(
            signal_type, conditions, f_score, current_price, latest_row, timeframe_analysis
        )

        # === 리스크 평가 ===
        risk_assessment = self._assess_risk(conditions, f_score, latest_row, timeframe_analysis)

        result = {
            "signal_type": signal_type,
            "signal_strength": signal_strength,
            "f_score": f_score,
            "conditions": conditions,
            "recommendations": recommendations,
            "risk_assessment": risk_assessment,
            "current_price": current_price,
            "generated_at": datetime.now().isoformat(),
        }

        # numpy/pandas 타입을 Python 기본 타입으로 변환
        return self._convert_to_native_types(result)

    def _check_conditions(
        self, f_score: int, latest_row: pd.Series, df: pd.DataFrame
    ) -> Dict[str, bool]:
        """매매 조건 체크"""
        conditions = {}

        # === 기본적 분석 조건 ===
        conditions["f_score_excellent"] = f_score >= 8  # F-Score 8-9점
        conditions["f_score_good"] = f_score >= 7  # F-Score 7점 이상
        conditions["f_score_poor"] = f_score < 7  # F-Score 7점 미만

        # === 기술적 분석 조건 ===

        # RSI 조건
        rsi = latest_row.get("rsi", 50)
        conditions["rsi_oversold"] = 30 <= rsi <= 50  # RSI 과매도~중립
        conditions["rsi_overbought"] = rsi > 70  # RSI 과매수
        conditions["rsi_neutral"] = 40 <= rsi <= 60  # RSI 중립

        # ADX 조건 (추세 강도)
        adx = latest_row.get("adx", 0)
        conditions["strong_trend"] = adx > 30  # 강한 추세
        conditions["weak_trend"] = adx < 20  # 약한 추세

        # Golden Cross / Death Cross
        if len(df) >= 2:
            sma_50_current = latest_row.get("sma_50", 0)
            sma_200_current = latest_row.get("sma_200", 0)
            sma_50_prev = df.iloc[-2].get("sma_50", 0)
            sma_200_prev = df.iloc[-2].get("sma_200", 0)

            # NaN 체크
            if not pd.isna([sma_50_current, sma_200_current, sma_50_prev, sma_200_prev]).any():
                conditions["golden_cross"] = (
                    sma_50_prev <= sma_200_prev
                ) and (sma_50_current > sma_200_current)
                conditions["death_cross"] = (
                    sma_50_prev >= sma_200_prev
                ) and (sma_50_current < sma_200_current)
            else:
                conditions["golden_cross"] = False
                conditions["death_cross"] = False
        else:
            conditions["golden_cross"] = False
            conditions["death_cross"] = False

        # 이동평균선 배열
        close = latest_row.get("close", 0)
        sma_20 = latest_row.get("sma_20", 0)
        sma_50 = latest_row.get("sma_50", 0)
        sma_200 = latest_row.get("sma_200", 0)

        if not pd.isna([close, sma_20, sma_50, sma_200]).any():
            conditions["above_ma20"] = close > sma_20
            conditions["above_ma50"] = close > sma_50
            conditions["above_ma200"] = close > sma_200
            conditions["bullish_alignment"] = (
                close > sma_20 > sma_50 > sma_200
            )  # 정배열
        else:
            conditions["above_ma20"] = False
            conditions["above_ma50"] = False
            conditions["above_ma200"] = False
            conditions["bullish_alignment"] = False

        # 볼륨 증가 (최근 거래량이 평균보다 50% 이상 증가)
        volume = latest_row.get("volume", 0)
        avg_volume_20 = df["volume"].rolling(window=20).mean().iloc[-1]
        if not pd.isna(avg_volume_20) and avg_volume_20 > 0:
            conditions["volume_surge"] = volume > avg_volume_20 * 1.5
        else:
            conditions["volume_surge"] = False

        # 변동성 체크
        atr_ratio = latest_row.get("atr_ratio", 0)
        conditions["high_volatility"] = atr_ratio > 0.03  # 3% 이상 변동성
        conditions["low_volatility"] = atr_ratio < 0.02  # 2% 미만 변동성

        return conditions

    def _integrate_timeframe_analysis(
        self, conditions: Dict[str, bool], timeframe_analysis: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        타임프레임 분석 결과를 조건에 통합

        타임프레임 정렬 상태에 따라 조건 가중치 조정
        """
        if not timeframe_analysis:
            return conditions

        alignment_status = timeframe_analysis.get("alignment_status")
        suitability = timeframe_analysis.get("trade_suitability", {})

        # 타임프레임 정렬 상태 조건 추가
        conditions["timeframe_aligned"] = alignment_status == "aligned"
        conditions["timeframe_partial_aligned"] = alignment_status == "partial_aligned"
        conditions["timeframe_conflicted"] = alignment_status == "conflicted"

        # 거래 적합성
        conditions["trade_suitable"] = suitability.get("should_trade", False)

        # 신뢰도
        conditions["high_confidence"] = suitability.get("confidence", 0) >= 70

        return conditions

    def _determine_signal_type(
        self, conditions: Dict[str, bool], f_score: int, timeframe_analysis: Optional[Dict[str, Any]] = None
    ) -> SignalType:
        """시그널 타입 결정 (타임프레임 분석 반영)"""

        # 타임프레임 충돌 시 거래 회피
        if timeframe_analysis and conditions.get("timeframe_conflicted", False):
            return SignalType.WARNING

        # 타임프레임 완전 정렬 + 강력한 기본 조건
        if conditions.get("timeframe_aligned", False):
            # STRONG BUY 조건 강화
            if (
                conditions["f_score_excellent"]
                and conditions["golden_cross"]
                and conditions["strong_trend"]
                and conditions["rsi_oversold"]
            ):
                return SignalType.STRONG_BUY

            # BUY 조건
            if conditions["f_score_good"] or (
                conditions["golden_cross"] and conditions["bullish_alignment"]
            ):
                return SignalType.BUY

            # STRONG SELL 조건
            if (
                f_score < 5
                and conditions["death_cross"]
                and conditions["rsi_overbought"]
            ):
                return SignalType.STRONG_SELL

            # SELL 조건
            if conditions["f_score_poor"] and conditions["death_cross"]:
                return SignalType.SELL

        # 부분 정렬 - 보수적 접근
        elif conditions.get("timeframe_partial_aligned", False):
            if conditions["f_score_good"] and conditions["golden_cross"]:
                return SignalType.BUY

            if conditions["f_score_poor"] or conditions["rsi_overbought"]:
                return SignalType.WARNING

        # 원래 로직 (타임프레임 분석 없을 때)
        else:
            if (
                conditions["f_score_excellent"]
                and conditions["golden_cross"]
                and conditions["strong_trend"]
                and conditions["rsi_oversold"]
                and conditions["volume_surge"]
            ):
                return SignalType.STRONG_BUY

            if conditions["f_score_good"] or (
                conditions["golden_cross"] and conditions["bullish_alignment"]
            ):
                return SignalType.BUY

            if (
                conditions["f_score_poor"]
                or conditions["rsi_overbought"]
                or conditions["weak_trend"]
            ):
                return SignalType.WARNING

            if conditions["f_score_poor"] and conditions["death_cross"]:
                return SignalType.SELL

            if (
                f_score < 5
                and conditions["death_cross"]
                and conditions["rsi_overbought"]
                and conditions["volume_surge"]
            ):
                return SignalType.STRONG_SELL

        return SignalType.HOLD

    def _calculate_signal_strength(
        self, conditions: Dict[str, bool], timeframe_analysis: Optional[Dict[str, Any]] = None
    ) -> SignalStrength:
        """시그널 강도 계산 (타임프레임 분석 반영)"""

        positive_conditions = sum(
            1
            for key, value in conditions.items()
            if value
            and key
            in [
                "f_score_excellent",
                "f_score_good",
                "golden_cross",
                "strong_trend",
                "rsi_oversold",
                "volume_surge",
                "bullish_alignment",
                "timeframe_aligned",
                "trade_suitable",
                "high_confidence",
            ]
        )

        # 타임프레임 정렬 시 가중치 증가
        if timeframe_analysis:
            alignment_status = timeframe_analysis.get("alignment_status")
            if alignment_status == "aligned":
                positive_conditions += 2  # 보너스 점수
            elif alignment_status == "partial_aligned":
                positive_conditions += 1

        if positive_conditions >= 7:
            return SignalStrength.VERY_STRONG
        elif positive_conditions >= 5:
            return SignalStrength.STRONG
        elif positive_conditions >= 3:
            return SignalStrength.MODERATE
        else:
            return SignalStrength.WEAK

    def _generate_recommendations(
        self,
        signal_type: SignalType,
        conditions: Dict[str, bool],
        f_score: int,
        current_price: float,
        latest_row: pd.Series,
        timeframe_analysis: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """추천 액션 생성 (타임프레임 분석 반영)"""

        recommendations = []

        # 타임프레임 분석 기반 추천
        if timeframe_analysis:
            suitability = timeframe_analysis.get("trade_suitability", {})
            recommendations.extend(suitability.get("recommendations", []))
            warnings = suitability.get("warnings", [])
            if warnings:
                recommendations.extend(warnings)

            # 진입점 최적화 추천
            entry_analysis = timeframe_analysis.get("entry_analysis")
            if entry_analysis and entry_analysis.get("entry_recommended"):
                recommendations.extend(entry_analysis.get("entry_strategy", []))

        # 기존 추천 로직 (타임프레임 없을 때)
        if signal_type == SignalType.STRONG_BUY:
            if not timeframe_analysis:
                recommendations.append("💪 강력 매수 추천")
            recommendations.append(f"진입가: ${current_price:.2f}")
            recommendations.append("포지션: 100% 투자")

        elif signal_type == SignalType.BUY:
            if not timeframe_analysis:
                recommendations.append("✅ 매수 추천")
            recommendations.append(f"진입가: ${current_price:.2f}")
            recommendations.append("포지션: 70% 투자")

        elif signal_type == SignalType.WARNING:
            if not timeframe_analysis:
                recommendations.append(f"⚠️ 주의 (F-Score: {f_score}/9)")
            recommendations.append("포지션 축소: 50%로 감소")

        elif signal_type == SignalType.SELL:
            if not timeframe_analysis:
                recommendations.append("📉 매도 권장")
            recommendations.append("포지션 정리: 전량 매도")

        elif signal_type == SignalType.STRONG_SELL:
            if not timeframe_analysis:
                recommendations.append("🚨 즉시 매도")
            recommendations.append("포지션 정리: 즉시 전량 매도")

        return recommendations

    def _assess_risk(
        self,
        conditions: Dict[str, bool],
        f_score: int,
        latest_row: pd.Series,
        timeframe_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """리스크 평가 (타임프레임 분석 반영)"""

        risk_factors = []
        risk_level = "low"

        # 타임프레임 리스크
        if timeframe_analysis:
            if conditions.get("timeframe_conflicted", False):
                risk_factors.append("🚫 타임프레임 충돌 - 높은 불확실성")
                risk_level = "high"
            elif conditions.get("timeframe_partial_aligned", False):
                risk_factors.append("🟡 타임프레임 부분 정렬 - 중간 위험도")
                if risk_level == "low":
                    risk_level = "medium"

        # F-Score 리스크
        if f_score < 7:
            risk_factors.append(f"낮은 F-Score ({f_score}/9) - 재무 건전성 부족")
            if risk_level == "low":
                risk_level = "medium"
            if f_score < 5:
                risk_level = "high"

        # RSI 리스크
        rsi = latest_row.get("rsi", 50)
        if not pd.isna(rsi):
            if rsi > 70:
                risk_factors.append(f"RSI 과매수 ({rsi:.1f}) - 조정 위험")
                if risk_level != "high":
                    risk_level = "medium"
            elif rsi < 30:
                risk_factors.append(f"RSI 과매도 ({rsi:.1f}) - 추가 하락 가능")

        # 변동성 리스크
        if conditions.get("high_volatility", False):
            risk_factors.append("높은 변동성 - 급격한 가격 변동 위험")

        if not risk_factors:
            risk_factors.append("✅ 리스크 요인 최소화")

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
        }


# 서비스 인스턴스
hybrid_signal_generator = HybridSignalGenerator()
