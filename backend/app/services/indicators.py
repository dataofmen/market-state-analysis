import pandas as pd
import numpy as np
from typing import Dict, Any, List


class TechnicalIndicators:
    """기술적 지표 계산 서비스"""

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        ATR (Average True Range) 계산

        Args:
            df: OHLC 데이터프레임 (high, low, close 컬럼 필요)
            period: 기간 (기본값: 14)

        Returns:
            ATR 시리즈
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]

        # True Range 계산
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # ATR 계산 (EMA)
        atr = tr.ewm(span=period, adjust=False).mean()

        return atr

    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame, period: int = 20, num_std: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        Bollinger Bands 계산

        Args:
            df: 가격 데이터프레임 (close 컬럼 필요)
            period: 기간 (기본값: 20)
            num_std: 표준편차 배수 (기본값: 2.0)

        Returns:
            upper, middle, lower 밴드 딕셔너리
        """
        close = df["close"]

        # Middle Band (SMA)
        middle = close.rolling(window=period).mean()

        # Standard Deviation
        std = close.rolling(window=period).std()

        # Upper and Lower Bands
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)

        return {"upper": upper, "middle": middle, "lower": lower}

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
        """
        ADX (Average Directional Index) 계산

        Args:
            df: OHLC 데이터프레임 (high, low, close 컬럼 필요)
            period: 기간 (기본값: 14)

        Returns:
            adx, plus_di, minus_di 딕셔너리
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]

        # +DM, -DM 계산
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Smoothed TR, +DM, -DM
        atr = tr.ewm(span=period, adjust=False).mean()
        plus_dm_smooth = plus_dm.ewm(span=period, adjust=False).mean()
        minus_dm_smooth = minus_dm.ewm(span=period, adjust=False).mean()

        # +DI, -DI
        plus_di = 100 * plus_dm_smooth / atr
        minus_di = 100 * minus_dm_smooth / atr

        # DX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

        # ADX
        adx = dx.ewm(span=period, adjust=False).mean()

        return {"adx": adx, "plus_di": plus_di, "minus_di": minus_di}

    @staticmethod
    def calculate_standard_deviation(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        표준편차 계산

        Args:
            df: 가격 데이터프레임 (close 컬럼 필요)
            period: 기간 (기본값: 20)

        Returns:
            표준편차 시리즈
        """
        return df["close"].rolling(window=period).std()

    @staticmethod
    def calculate_all_indicators(
        price_data: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        모든 기술적 지표를 한 번에 계산

        Args:
            price_data: FMP API에서 받은 가격 데이터 리스트
                       [{date, open, high, low, close, volume}, ...]

        Returns:
            모든 지표가 포함된 데이터프레임
        """
        # 데이터프레임 생성
        df = pd.DataFrame(price_data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        # ATR 계산
        df["atr"] = TechnicalIndicators.calculate_atr(df, period=14)
        df["atr_ratio"] = df["atr"] / df["close"]

        # Bollinger Bands 계산
        bb = TechnicalIndicators.calculate_bollinger_bands(df, period=20, num_std=2.0)
        df["bb_upper"] = bb["upper"]
        df["bb_middle"] = bb["middle"]
        df["bb_lower"] = bb["lower"]
        df["bb_width"] = df["bb_upper"] - df["bb_lower"]
        df["bb_width_ratio"] = df["bb_width"] / df["close"]

        # ADX 계산
        adx = TechnicalIndicators.calculate_adx(df, period=14)
        df["adx"] = adx["adx"]
        df["plus_di"] = adx["plus_di"]
        df["minus_di"] = adx["minus_di"]

        # Standard Deviation 계산
        df["std_dev"] = TechnicalIndicators.calculate_standard_deviation(df, period=20)

        return df


# 서비스 인스턴스
indicators_service = TechnicalIndicators()
