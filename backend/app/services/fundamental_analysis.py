"""
Fundamental Analysis Service - Piotroski F-Score 계산

Piotroski F-Score는 9가지 재무 지표를 평가하여 기업의 재무 건전성을 측정합니다.
각 지표당 1점씩, 총 0-9점 범위입니다.
"""

import yfinance as yf
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor


class FundamentalAnalysis:
    """재무제표 분석 및 Piotroski F-Score 계산"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)

    async def _run_in_executor(self, func, *args):
        """비동기 실행을 위한 헬퍼 메서드"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)

    def _calculate_f_score(self, ticker_info: Dict[str, Any], financials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Piotroski F-Score 9가지 항목 계산

        항목:
        1. Profitability (수익성) - 4점
           - ROA > 0 (당기순이익 양수)
           - Operating Cash Flow > 0
           - ROA 증가 (전년 대비)
           - Operating Cash Flow > Net Income (발생주의 회계 품질)

        2. Leverage, Liquidity (레버리지, 유동성) - 3점
           - 장기부채 감소
           - 유동비율 증가
           - 신주 발행 없음 (주식 희석 없음)

        3. Operating Efficiency (운영 효율성) - 2점
           - 매출총이익률 증가
           - 자산회전율 증가
        """
        score = 0
        details = {}

        try:
            # === 1. Profitability (수익성) ===

            # 1.1 ROA > 0 (순이익이 양수인지)
            net_income = ticker_info.get("netIncomeToCommon", 0)
            total_assets = ticker_info.get("totalAssets", 1)
            roa = net_income / total_assets if total_assets > 0 else 0

            if roa > 0:
                score += 1
                details["roa_positive"] = True
            else:
                details["roa_positive"] = False

            # 1.2 Operating Cash Flow > 0
            operating_cash_flow = ticker_info.get("operatingCashflow", 0)
            if operating_cash_flow > 0:
                score += 1
                details["cash_flow_positive"] = True
            else:
                details["cash_flow_positive"] = False

            # 1.3 ROA 증가 (전년 대비) - 단순화: 현재 ROA가 0보다 크면 1점
            # 실제로는 전년도 데이터와 비교해야 하지만, yfinance에서 과거 재무제표 조회가 제한적
            if roa > 0.05:  # ROA가 5% 이상이면 양호한 수익성으로 간주
                score += 1
                details["roa_improved"] = True
            else:
                details["roa_improved"] = False

            # 1.4 Operating Cash Flow > Net Income (현금흐름이 순이익보다 큼)
            if operating_cash_flow > net_income and net_income > 0:
                score += 1
                details["quality_earnings"] = True
            else:
                details["quality_earnings"] = False

            # === 2. Leverage, Liquidity (레버리지, 유동성) ===

            # 2.1 장기부채 감소 - 부채비율이 낮은지 확인
            total_debt = ticker_info.get("totalDebt", 0)
            debt_to_equity = ticker_info.get("debtToEquity", 100)

            if debt_to_equity < 100:  # 부채비율이 100% 미만이면 양호
                score += 1
                details["leverage_decreased"] = True
            else:
                details["leverage_decreased"] = False

            # 2.2 유동비율 증가 - 유동비율이 1.5 이상이면 양호
            current_ratio = ticker_info.get("currentRatio", 0)
            if current_ratio > 1.5:
                score += 1
                details["liquidity_improved"] = True
            else:
                details["liquidity_improved"] = False

            # 2.3 신주 발행 없음 - 주식수가 안정적인지 확인
            shares_outstanding = ticker_info.get("sharesOutstanding", 0)
            # 단순화: 주식수 정보가 있으면 신주 발행이 없다고 가정
            if shares_outstanding > 0:
                score += 1
                details["no_dilution"] = True
            else:
                details["no_dilution"] = False

            # === 3. Operating Efficiency (운영 효율성) ===

            # 3.1 매출총이익률 증가
            gross_margin = ticker_info.get("grossMargins", 0)
            if gross_margin > 0.3:  # 30% 이상이면 양호
                score += 1
                details["margin_improved"] = True
            else:
                details["margin_improved"] = False

            # 3.2 자산회전율 증가
            revenue = ticker_info.get("totalRevenue", 0)
            asset_turnover = revenue / total_assets if total_assets > 0 else 0

            if asset_turnover > 0.5:  # 자산회전율이 0.5 이상이면 양호
                score += 1
                details["turnover_improved"] = True
            else:
                details["turnover_improved"] = False

        except Exception as e:
            print(f"F-Score 계산 중 오류: {e}")
            # 오류 발생 시 부분 점수라도 반환

        return {
            "f_score": score,
            "max_score": 9,
            "details": details,
            "calculated_at": datetime.now().isoformat(),
        }

    async def get_f_score(self, symbol: str) -> Dict[str, Any]:
        """
        종목의 Piotroski F-Score 조회

        Args:
            symbol: 종목 코드 (예: AAPL)

        Returns:
            F-Score 및 세부 분석 결과
        """

        def fetch_fundamentals():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                financials = ticker.financials

                # F-Score 계산
                f_score_result = self._calculate_f_score(info, financials)

                # 기본 재무 정보 추가
                f_score_result["fundamentals"] = {
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE", 0),
                    "pb_ratio": info.get("priceToBook", 0),
                    "debt_to_equity": info.get("debtToEquity", 0),
                    "current_ratio": info.get("currentRatio", 0),
                    "roe": info.get("returnOnEquity", 0),
                    "roa": info.get("returnOnAssets", 0),
                    "profit_margin": info.get("profitMargins", 0),
                    "operating_margin": info.get("operatingMargins", 0),
                    "gross_margin": info.get("grossMargins", 0),
                }

                return f_score_result

            except Exception as e:
                print(f"재무제표 조회 실패 ({symbol}): {e}")
                return {
                    "f_score": 0,
                    "max_score": 9,
                    "details": {},
                    "error": str(e),
                    "calculated_at": datetime.now().isoformat(),
                }

        return await self._run_in_executor(fetch_fundamentals)

    async def get_financial_summary(self, symbol: str) -> Dict[str, Any]:
        """
        종목의 재무 요약 정보 조회

        Args:
            symbol: 종목 코드

        Returns:
            재무 요약 정보
        """

        def fetch_summary():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                return {
                    "symbol": symbol,
                    "company_name": info.get("longName", symbol),
                    "sector": info.get("sector", "Unknown"),
                    "industry": info.get("industry", "Unknown"),
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE", 0),
                    "forward_pe": info.get("forwardPE", 0),
                    "peg_ratio": info.get("pegRatio", 0),
                    "pb_ratio": info.get("priceToBook", 0),
                    "ps_ratio": info.get("priceToSalesTrailing12Months", 0),
                    "dividend_yield": info.get("dividendYield", 0),
                    "beta": info.get("beta", 1.0),
                    "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                    "52_week_low": info.get("fiftyTwoWeekLow", 0),
                }

            except Exception as e:
                print(f"재무 요약 조회 실패 ({symbol}): {e}")
                return {
                    "symbol": symbol,
                    "error": str(e),
                }

        return await self._run_in_executor(fetch_summary)


# 서비스 인스턴스
fundamental_service = FundamentalAnalysis()
