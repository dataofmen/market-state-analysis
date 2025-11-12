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
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        RSI (Relative Strength Index) 계산

        Args:
            df: 가격 데이터프레임 (close 컬럼 필요)
            period: 기간 (기본값: 14)

        Returns:
            RSI 시리즈 (0-100)
        """
        close = df["close"]

        # 가격 변화 계산
        delta = close.diff()

        # 상승/하락 분리
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 평균 상승/하락 계산 (EMA)
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()

        # RS와 RSI 계산
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_moving_averages(df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        이동평균선 계산 (SMA, EMA)

        Args:
            df: 가격 데이터프레임 (close 컬럼 필요)

        Returns:
            SMA/EMA 딕셔너리 (20일, 50일, 200일)
        """
        close = df["close"]

        return {
            "sma_20": close.rolling(window=20).mean(),
            "sma_50": close.rolling(window=50).mean(),
            "sma_200": close.rolling(window=200).mean(),
            "ema_12": close.ewm(span=12, adjust=False).mean(),
            "ema_26": close.ewm(span=26, adjust=False).mean(),
        }

    @staticmethod
    def detect_golden_death_cross(df: pd.DataFrame) -> Dict[str, bool]:
        """
        Golden Cross / Death Cross 감지

        Args:
            df: 이동평균선이 포함된 데이터프레임

        Returns:
            golden_cross, death_cross 여부 딕셔너리
        """
        # 최근 데이터 확인
        if len(df) < 2:
            return {"golden_cross": False, "death_cross": False}

        # 50일선과 200일선 교차 확인
        sma_50_current = df["sma_50"].iloc[-1]
        sma_200_current = df["sma_200"].iloc[-1]
        sma_50_prev = df["sma_50"].iloc[-2]
        sma_200_prev = df["sma_200"].iloc[-2]

        # NaN 체크
        if pd.isna([sma_50_current, sma_200_current, sma_50_prev, sma_200_prev]).any():
            return {"golden_cross": False, "death_cross": False}

        # Golden Cross: 50일선이 200일선을 상향 돌파
        golden_cross = (sma_50_prev <= sma_200_prev) and (sma_50_current > sma_200_current)

        # Death Cross: 50일선이 200일선을 하향 돌파
        death_cross = (sma_50_prev >= sma_200_prev) and (sma_50_current < sma_200_current)

        return {"golden_cross": golden_cross, "death_cross": death_cross}

    @staticmethod
    def analyze_volume(df: pd.DataFrame, period: int = 20) -> Dict[str, Any]:
        """
        거래량 분석

        Args:
            df: 가격 데이터프레임 (volume 컬럼 필요)
            period: 기간 (기본값: 20)

        Returns:
            거래량 분석 결과 딕셔너리
        """
        volume = df["volume"]

        # 평균 거래량
        avg_volume = volume.rolling(window=period).mean()

        # 최근 거래량이 평균보다 높은지
        current_volume = volume.iloc[-1]
        avg_volume_current = avg_volume.iloc[-1]

        if pd.isna(avg_volume_current):
            volume_ratio = 1.0
            volume_increase = False
        else:
            volume_ratio = current_volume / avg_volume_current
            volume_increase = volume_ratio > 1.5  # 50% 이상 증가

        return {
            "current_volume": int(current_volume),
            "avg_volume": int(avg_volume_current) if not pd.isna(avg_volume_current) else 0,
            "volume_ratio": float(volume_ratio),
            "volume_increase": volume_increase,
        }

    @staticmethod
    def calculate_all_indicators(
        price_data: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        모든 기술적 지표를 한 번에 계산

        Args:
            price_data: Yahoo Finance에서 받은 가격 데이터 리스트
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

        # RSI 계산
        df["rsi"] = TechnicalIndicators.calculate_rsi(df, period=14)

        # 이동평균선 계산
        ma = TechnicalIndicators.calculate_moving_averages(df)
        df["sma_20"] = ma["sma_20"]
        df["sma_50"] = ma["sma_50"]
        df["sma_200"] = ma["sma_200"]
        df["ema_12"] = ma["ema_12"]
        df["ema_26"] = ma["ema_26"]

        return df


# 서비스 인스턴스
indicators_service = TechnicalIndicators()
