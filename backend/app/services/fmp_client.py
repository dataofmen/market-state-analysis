import yfinance as yf
from typing import List, Dict, Any
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor


class YFinanceClient:
    """Yahoo Finance API Client using yfinance library"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def _run_in_executor(self, func, *args):
        """비동기 실행을 위한 헬퍼 메서드"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)

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
            가격 데이터 리스트 (FMP 형식과 호환)
        """
        def fetch_data():
            ticker = yf.Ticker(symbol)

            # 기간 설정
            if from_date and to_date:
                start = from_date
                end = to_date
            else:
                # 기본값: 최근 90일
                end = datetime.now().strftime("%Y-%m-%d")
                start = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

            # 데이터 가져오기
            df = ticker.history(start=start, end=end)

            if df.empty:
                return []

            # FMP 형식으로 변환
            result = []
            for index, row in df.iterrows():
                result.append({
                    "date": index.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                })

            # 날짜 역순 정렬 (최신이 먼저)
            result.reverse()
            return result

        return await self._run_in_executor(fetch_data)

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        실시간 시세 조회

        Args:
            symbol: 종목 심볼 (e.g., "AAPL")

        Returns:
            실시간 시세 데이터
        """
        def fetch_quote():
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "changesPercentage": info.get("regularMarketChangePercent", 0),
                "change": info.get("regularMarketChange", 0),
                "dayLow": info.get("dayLow", 0),
                "dayHigh": info.get("dayHigh", 0),
                "yearHigh": info.get("fiftyTwoWeekHigh", 0),
                "yearLow": info.get("fiftyTwoWeekLow", 0),
                "marketCap": info.get("marketCap", 0),
                "volume": info.get("volume", 0),
                "avgVolume": info.get("averageVolume", 0),
                "open": info.get("open", 0),
                "previousClose": info.get("previousClose", 0),
            }

        return await self._run_in_executor(fetch_quote)

    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """
        기업 프로필 조회

        Args:
            symbol: 종목 심볼 (e.g., "AAPL")

        Returns:
            기업 프로필 데이터
        """
        def fetch_profile():
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "companyName": info.get("longName", symbol),
                "exchangeShortName": info.get("exchange", ""),
                "industry": info.get("industry", ""),
                "sector": info.get("sector", ""),
                "country": info.get("country", ""),
                "website": info.get("website", ""),
                "description": info.get("longBusinessSummary", ""),
                "ceo": info.get("companyOfficers", [{}])[0].get("name", "") if info.get("companyOfficers") else "",
                "fullTimeEmployees": info.get("fullTimeEmployees", 0),
                "address": info.get("address1", ""),
                "city": info.get("city", ""),
                "state": info.get("state", ""),
                "zip": info.get("zip", ""),
                "phone": info.get("phone", ""),
            }

        return await self._run_in_executor(fetch_profile)

    async def search_symbols(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        종목 검색

        Args:
            query: 검색 쿼리
            limit: 최대 결과 수

        Returns:
            검색 결과 리스트
        """
        def search():
            # yfinance는 직접 검색 기능이 없으므로,
            # 주요 종목 리스트에서 매칭하거나 단순히 심볼로 조회
            # 여기서는 단순히 쿼리를 심볼로 가정하고 조회
            try:
                ticker = yf.Ticker(query.upper())
                info = ticker.info

                if info.get("regularMarketPrice") or info.get("currentPrice"):
                    return [{
                        "symbol": query.upper(),
                        "name": info.get("longName", query.upper()),
                        "stockExchange": info.get("exchange", ""),
                        "currency": info.get("currency", "USD"),
                        "exchangeShortName": info.get("exchange", ""),
                    }]
            except Exception:
                pass

            return []

        return await self._run_in_executor(search)

    async def get_market_index(self, index: str = "^GSPC") -> Dict[str, Any]:
        """
        시장 지수 조회 (S&P 500, NASDAQ 등)

        Args:
            index: 지수 심볼 (^GSPC for S&P 500, ^IXIC for NASDAQ)

        Returns:
            지수 데이터
        """
        def fetch_index():
            ticker = yf.Ticker(index)
            info = ticker.info

            return {
                "symbol": index,
                "name": info.get("longName", index),
                "price": info.get("regularMarketPrice", 0),
                "changesPercentage": info.get("regularMarketChangePercent", 0),
                "change": info.get("regularMarketChange", 0),
            }

        return await self._run_in_executor(fetch_index)

    async def get_vix(self) -> float:
        """
        VIX (Volatility Index) 조회

        Returns:
            VIX 값
        """
        def fetch_vix():
            ticker = yf.Ticker("^VIX")
            info = ticker.info
            return float(info.get("regularMarketPrice", 0))

        return await self._run_in_executor(fetch_vix)


# FMP Client를 YFinance Client로 교체 (하위 호환성 유지)
fmp_client = YFinanceClient()
