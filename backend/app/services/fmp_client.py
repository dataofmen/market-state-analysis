import httpx
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings


class FMPClient:
    """Financial Modeling Prep API Client"""

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self):
        self.api_key = settings.FMP_API_KEY

    async def get_historical_prices(
        self, symbol: str, from_date: str = None, to_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        종목의 역사적 가격 데이터 조회

        Args:
            symbol: 종목 심볼 (e.g., "AAPL")
            from_date: 시작일 (YYYY-MM-DD)
            to_date: 종료일 (YYYY-MM-DD)

        Returns:
            가격 데이터 리스트
        """
        url = f"{self.BASE_URL}/historical-price-full/{symbol}"
        params = {"apikey": self.api_key}

        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("historical", [])

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        실시간 시세 조회

        Args:
            symbol: 종목 심볼 (e.g., "AAPL")

        Returns:
            실시간 시세 데이터
        """
        url = f"{self.BASE_URL}/quote/{symbol}"
        params = {"apikey": self.api_key}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}

    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """
        기업 프로필 조회

        Args:
            symbol: 종목 심볼 (e.g., "AAPL")

        Returns:
            기업 프로필 데이터
        """
        url = f"{self.BASE_URL}/profile/{symbol}"
        params = {"apikey": self.api_key}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}

    async def search_symbols(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        종목 검색

        Args:
            query: 검색 쿼리
            limit: 최대 결과 수

        Returns:
            검색 결과 리스트
        """
        url = f"{self.BASE_URL}/search"
        params = {"query": query, "limit": limit, "apikey": self.api_key}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def get_market_index(self, index: str = "^GSPC") -> Dict[str, Any]:
        """
        시장 지수 조회 (S&P 500, NASDAQ 등)

        Args:
            index: 지수 심볼 (^GSPC for S&P 500, ^IXIC for NASDAQ)

        Returns:
            지수 데이터
        """
        url = f"{self.BASE_URL}/quote/{index}"
        params = {"apikey": self.api_key}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}

    async def get_vix(self) -> float:
        """
        VIX (Volatility Index) 조회

        Returns:
            VIX 값
        """
        vix_data = await self.get_market_index("^VIX")
        return vix_data.get("price", 0.0)


# FMP Client 인스턴스
fmp_client = FMPClient()
