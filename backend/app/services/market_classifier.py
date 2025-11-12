from typing import Dict, Tuple
from enum import Enum


class TrendType(str, Enum):
    """추세 유형"""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    RANGE = "range"


class VolatilityLevel(str, Enum):
    """변동성 레벨"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EXTREME = "extreme"


class RiskLevel(str, Enum):
    """위험 레벨"""
    STABLE = "stable"
    CAUTION = "caution"
    ALERT = "alert"
    DANGER = "danger"


class MarketClassifier:
    """시장 상태 분류 서비스"""

    # 임계값 설정
    ADX_THRESHOLD_STRONG = 25  # 강한 추세
    ADX_THRESHOLD_WEAK = 20    # 약한 추세

    ATR_RATIO_LOW = 0.02       # 낮은 변동성
    ATR_RATIO_NORMAL = 0.03    # 보통 변동성
    ATR_RATIO_HIGH = 0.05      # 높은 변동성

    VIX_LOW = 15               # 안정
    VIX_CAUTION = 20           # 주의
    VIX_ALERT = 30             # 경고

    @staticmethod
    def classify_trend(
        adx: float,
        plus_di: float,
        minus_di: float,
        bb_width_ratio: float,
    ) -> TrendType:
        """
        추세 분류

        Args:
            adx: ADX 값
            plus_di: +DI 값
            minus_di: -DI 값
            bb_width_ratio: Bollinger Band Width Ratio

        Returns:
            추세 유형 (uptrend, downtrend, range)
        """
        # ADX가 낮으면 횡보
        if adx < MarketClassifier.ADX_THRESHOLD_WEAK:
            return TrendType.RANGE

        # Bollinger Band Width가 좁으면 횡보
        if bb_width_ratio < 0.04:
            return TrendType.RANGE

        # ADX가 높고 +DI > -DI면 상승 추세
        if adx >= MarketClassifier.ADX_THRESHOLD_WEAK:
            if plus_di > minus_di:
                return TrendType.UPTREND
            else:
                return TrendType.DOWNTREND

        return TrendType.RANGE

    @staticmethod
    def classify_volatility(atr_ratio: float, std_dev_ratio: float) -> VolatilityLevel:
        """
        변동성 분류

        Args:
            atr_ratio: ATR / Price 비율
            std_dev_ratio: StdDev / Price 비율

        Returns:
            변동성 레벨
        """
        # 평균 변동성 지표
        avg_volatility = (atr_ratio + std_dev_ratio) / 2

        if avg_volatility < MarketClassifier.ATR_RATIO_LOW:
            return VolatilityLevel.LOW
        elif avg_volatility < MarketClassifier.ATR_RATIO_NORMAL:
            return VolatilityLevel.NORMAL
        elif avg_volatility < MarketClassifier.ATR_RATIO_HIGH:
            return VolatilityLevel.HIGH
        else:
            return VolatilityLevel.EXTREME

    @staticmethod
    def classify_risk(vix: float, volatility_level: VolatilityLevel) -> RiskLevel:
        """
        위험도 분류

        Args:
            vix: VIX 지수
            volatility_level: 변동성 레벨

        Returns:
            위험 레벨
        """
        # VIX 기반 기본 위험도
        if vix < MarketClassifier.VIX_LOW:
            base_risk = RiskLevel.STABLE
        elif vix < MarketClassifier.VIX_CAUTION:
            base_risk = RiskLevel.CAUTION
        elif vix < MarketClassifier.VIX_ALERT:
            base_risk = RiskLevel.ALERT
        else:
            base_risk = RiskLevel.DANGER

        # 변동성 레벨로 조정
        if volatility_level == VolatilityLevel.EXTREME:
            if base_risk == RiskLevel.STABLE:
                return RiskLevel.CAUTION
            elif base_risk == RiskLevel.CAUTION:
                return RiskLevel.ALERT
            else:
                return RiskLevel.DANGER

        return base_risk

    @staticmethod
    def recommend_strategy(
        trend_type: TrendType,
        volatility_level: VolatilityLevel,
        risk_level: RiskLevel,
    ) -> Tuple[str, float]:
        """
        전략 추천

        Args:
            trend_type: 추세 유형
            volatility_level: 변동성 레벨
            risk_level: 위험 레벨

        Returns:
            (전략명, 포지션 크기 비율)
        """
        # 위험도에 따른 기본 포지션 크기
        position_size_map = {
            RiskLevel.STABLE: 1.0,
            RiskLevel.CAUTION: 0.75,
            RiskLevel.ALERT: 0.5,
            RiskLevel.DANGER: 0.25,
        }
        base_position_size = position_size_map[risk_level]

        # 추세 + 변동성 조합별 전략
        if trend_type == TrendType.UPTREND:
            if volatility_level in [VolatilityLevel.LOW, VolatilityLevel.NORMAL]:
                return ("trend_following", base_position_size * 1.2)
            else:
                return ("swing_trading", base_position_size * 0.8)

        elif trend_type == TrendType.DOWNTREND:
            if volatility_level in [VolatilityLevel.LOW, VolatilityLevel.NORMAL]:
                return ("short_selling", base_position_size * 0.8)
            else:
                return ("cash_position", 0.0)

        else:  # RANGE
            if volatility_level == VolatilityLevel.LOW:
                return ("mean_reversion", base_position_size * 1.0)
            elif volatility_level == VolatilityLevel.NORMAL:
                return ("range_trading", base_position_size * 0.9)
            else:
                return ("wait_and_see", base_position_size * 0.3)

    @staticmethod
    def classify_market_state(indicators: Dict) -> Dict:
        """
        전체 시장 상태 분류

        Args:
            indicators: 기술적 지표 딕셔너리
                {
                    'adx': float,
                    'plus_di': float,
                    'minus_di': float,
                    'atr_ratio': float,
                    'bb_width_ratio': float,
                    'std_dev': float,
                    'close': float,
                    'vix': float (optional)
                }

        Returns:
            시장 상태 분류 결과
        """
        # 추세 분류
        trend_type = MarketClassifier.classify_trend(
            adx=indicators["adx"],
            plus_di=indicators["plus_di"],
            minus_di=indicators["minus_di"],
            bb_width_ratio=indicators["bb_width_ratio"],
        )

        # 변동성 분류
        std_dev_ratio = indicators["std_dev"] / indicators["close"]
        volatility_level = MarketClassifier.classify_volatility(
            atr_ratio=indicators["atr_ratio"],
            std_dev_ratio=std_dev_ratio,
        )

        # 위험도 분류
        vix = indicators.get("vix", 15.0)  # VIX 기본값 15
        risk_level = MarketClassifier.classify_risk(
            vix=vix,
            volatility_level=volatility_level,
        )

        # 전략 추천
        strategy, position_size = MarketClassifier.recommend_strategy(
            trend_type=trend_type,
            volatility_level=volatility_level,
            risk_level=risk_level,
        )

        return {
            "trend_type": trend_type.value,
            "volatility_level": volatility_level.value,
            "risk_level": risk_level.value,
            "recommended_strategy": strategy,
            "position_sizing_ratio": round(position_size, 2),
        }


# 서비스 인스턴스
market_classifier = MarketClassifier()
