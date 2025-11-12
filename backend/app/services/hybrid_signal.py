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
    ) -> Dict[str, Any]:
        """
        종합 매매 시그널 생성

        Args:
            f_score_data: Piotroski F-Score 데이터
            technical_data: 기술적 지표 데이터프레임
            current_price: 현재 가격

        Returns:
            시그널 정보 딕셔너리
        """
        f_score = f_score_data.get("f_score", 0)
        latest_row = technical_data.iloc[-1]

        # === 시그널 조건 체크 ===
        conditions = self._check_conditions(f_score, latest_row, technical_data)

        # === 시그널 타입 결정 ===
        signal_type = self._determine_signal_type(conditions, f_score)

        # === 시그널 강도 계산 ===
        signal_strength = self._calculate_signal_strength(conditions)

        # === 추천 액션 생성 ===
        recommendations = self._generate_recommendations(
            signal_type, conditions, f_score, current_price, latest_row
        )

        # === 리스크 평가 ===
        risk_assessment = self._assess_risk(conditions, f_score, latest_row)

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

    def _determine_signal_type(
        self, conditions: Dict[str, bool], f_score: int
    ) -> SignalType:
        """시그널 타입 결정"""

        # === STRONG BUY 조건 ===
        # F-Score 8-9 + Golden Cross + 강한 추세 + RSI 과매도~중립 + 볼륨 증가
        if (
            conditions["f_score_excellent"]
            and conditions["golden_cross"]
            and conditions["strong_trend"]
            and conditions["rsi_oversold"]
            and conditions["volume_surge"]
        ):
            return SignalType.STRONG_BUY

        # === BUY 조건 ===
        # F-Score 7+ 또는 (Golden Cross + 정배열)
        if conditions["f_score_good"] or (
            conditions["golden_cross"] and conditions["bullish_alignment"]
        ):
            return SignalType.BUY

        # === WARNING 조건 ===
        # F-Score 하락 또는 RSI 과매수 지속 또는 ADX 하락
        if (
            conditions["f_score_poor"]
            or conditions["rsi_overbought"]
            or conditions["weak_trend"]
        ):
            return SignalType.WARNING

        # === SELL 조건 ===
        # F-Score < 7 + Death Cross
        if conditions["f_score_poor"] and conditions["death_cross"]:
            return SignalType.SELL

        # === STRONG SELL 조건 ===
        # F-Score < 5 + Death Cross + RSI 과매수 + 볼륨 증가 (공포 매도)
        if (
            f_score < 5
            and conditions["death_cross"]
            and conditions["rsi_overbought"]
            and conditions["volume_surge"]
        ):
            return SignalType.STRONG_SELL

        # 기본값: HOLD
        return SignalType.HOLD

    def _calculate_signal_strength(self, conditions: Dict[str, bool]) -> SignalStrength:
        """시그널 강도 계산"""

        # 긍정적 조건 카운트
        positive_conditions = [
            "f_score_excellent",
            "f_score_good",
            "golden_cross",
            "strong_trend",
            "rsi_oversold",
            "bullish_alignment",
            "volume_surge",
            "above_ma200",
        ]

        count = sum(1 for cond in positive_conditions if conditions.get(cond, False))

        if count >= 5:
            return SignalStrength.VERY_STRONG
        elif count >= 4:
            return SignalStrength.STRONG
        elif count >= 3:
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
    ) -> List[str]:
        """추천 액션 생성"""
        recommendations = []

        if signal_type == SignalType.STRONG_BUY:
            recommendations.append(f"💎 강력 매수 추천 (F-Score: {f_score}/9)")
            recommendations.append("진입 시기: 즉시 진입 가능")
            recommendations.append("포지션 크기: 100% (전액 투자)")

            # 목표가 계산 (현재가 기준 +15%)
            target_price = current_price * 1.15
            recommendations.append(f"목표가: ${target_price:.2f} (+15%)")

            # 손절가 계산 (현재가 기준 -7%)
            stop_loss = current_price * 0.93
            recommendations.append(f"손절가: ${stop_loss:.2f} (-7%)")

        elif signal_type == SignalType.BUY:
            recommendations.append(f"✅ 매수 추천 (F-Score: {f_score}/9)")
            recommendations.append("진입 시기: 조정 시 분할 매수")
            recommendations.append("포지션 크기: 70-80%")

            target_price = current_price * 1.10
            recommendations.append(f"목표가: ${target_price:.2f} (+10%)")

            stop_loss = current_price * 0.95
            recommendations.append(f"손절가: ${stop_loss:.2f} (-5%)")

        elif signal_type == SignalType.HOLD:
            recommendations.append("⏸️ 보유 유지")
            recommendations.append("관망: 추가 시그널 대기")

            if conditions["rsi_overbought"]:
                recommendations.append("⚠️ RSI 과매수 구간 - 익절 고려")

        elif signal_type == SignalType.WARNING:
            recommendations.append(f"⚠️ 주의 (F-Score: {f_score}/9)")
            recommendations.append("포지션 축소: 50%로 감소")
            recommendations.append("손절 준비: 손절가 상향 조정")

            if conditions["death_cross"]:
                recommendations.append("🔴 Death Cross 발생 - 청산 고려")

        elif signal_type == SignalType.SELL:
            recommendations.append(f"📉 매도 추천 (F-Score: {f_score}/9)")
            recommendations.append("포지션 정리: 전량 매도")
            recommendations.append("재진입: F-Score 개선 및 Golden Cross 발생 시")

        elif signal_type == SignalType.STRONG_SELL:
            recommendations.append(f"🚨 긴급 매도 (F-Score: {f_score}/9)")
            recommendations.append("즉시 청산: 지체 없이 전량 매도")
            recommendations.append("공매도 고려 가능 (고급 투자자)")

        return recommendations

    def _assess_risk(
        self, conditions: Dict[str, bool], f_score: int, latest_row: pd.Series
    ) -> Dict[str, Any]:
        """리스크 평가"""

        risk_level = "low"
        risk_factors = []

        # F-Score 리스크
        if f_score < 7:
            risk_level = "high"
            risk_factors.append(f"낮은 F-Score ({f_score}/9) - 재무 건전성 부족")

        # 기술적 리스크
        if conditions["death_cross"]:
            risk_level = "high"
            risk_factors.append("Death Cross 발생 - 장기 하락 추세 전환")

        if conditions["rsi_overbought"]:
            if risk_level == "low":
                risk_level = "medium"
            risk_factors.append("RSI 과매수 - 단기 조정 가능성")

        if conditions["high_volatility"]:
            if risk_level == "low":
                risk_level = "medium"
            risk_factors.append("높은 변동성 - 급격한 가격 변동 위험")

        if not risk_factors:
            risk_factors.append("리스크 요인 없음 - 안정적 투자 환경")

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
        }


# 서비스 인스턴스
hybrid_signal_generator = HybridSignalGenerator()
