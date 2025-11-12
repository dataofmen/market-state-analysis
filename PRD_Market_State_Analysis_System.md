# PRD: 시장 상태 판단 시스템
## Market State Analysis System for Trading

**문서 버전**: 2.0
**작성일**: 2025-11-12
**최종 수정**: 2025-11-12
**프로젝트 코드**: 7412-PRD
**배포 플랫폼**: Railway.app

---

## 📋 Executive Summary

### 목적
미국 주식 시장의 상태(상승장/하락장/횡보장)와 변동성 수준을 자동으로 판단하여, 데이터 기반 투자 의사결정을 지원하는 시스템을 구축합니다.

### 핵심 가치 제안
- **객관적 시장 상태 판단**: 감정이 아닌 지표 기반 판단
- **리스크 관리 강화**: 변동성에 따른 포지션 사이징 자동화
- **거래 성과 분석**: 시장 상태별 수익률 추적 및 개선

### 목표 사용자
- 미국 주식 시장 투자자
- 시스템 트레이딩 실천자
- 데이터 기반 투자 의사결정을 원하는 개인 투자자

### 배포 환경
- **플랫폼**: Railway.app
- **형태**: 전용 웹 애플리케이션
- **접근**: 웹 브라우저 (Desktop/Mobile 반응형)

---

## 🎯 Problem Statement

### 현재 문제점
1. **주관적 시장 판단**: 감정에 따른 비일관적 의사결정
2. **변동성 무시**: 시장 상황과 무관한 동일한 전략 적용
3. **성과 분석 부족**: 어떤 시장 상태에서 수익/손실이 발생하는지 불명확
4. **수동 데이터 관리**: 지표 계산 및 기록의 번거로움

### 해결 방안
기술적 지표 기반 자동화 시스템으로 시장 상태를 객관적으로 판단하고, 매매 의사결정 시 활용할 수 있는 데이터를 제공합니다.

---

## 👥 User Personas

### Primary Persona: 시스템 트레이더
- **배경**: 미국 주식 투자 경험 1년 이상
- **목표**: 안정적이고 재현 가능한 수익 창출
- **Pain Points**:
  - 언제 진입/청산해야 할지 판단 어려움
  - 변동성이 큰 시장에서 손실 확대
  - 횡보장에서 빈번한 손절
- **Needs**:
  - 시장 상태에 따른 명확한 진입/청산 규칙
  - 자동화된 리스크 관리
  - 과거 거래 데이터 분석

---

## 🔧 Technical Indicators Specification

### 1. Average True Range (ATR)

#### 개요
일정 기간 내 가격 변화 폭을 평균화한 변동성 지표

#### 계산 방식
```
True Range (TR) = MAX(
  High - Low,
  |High - Previous Close|,
  |Low - Previous Close|
)

ATR = Moving Average of TR (일반적으로 14일)
```

#### 활용 방법
- **변동성 수준 판단**: ATR 값의 절대값 및 최근 평균 대비 비율
- **포지션 사이징**: ATR 기반 손절폭 설정
- **진입 조건**: 변동성이 일정 수준 이상일 때만 진입

#### 구현 요구사항
- 기본 기간: 14일 (사용자 설정 가능)
- 계산 결과: 절대값, 최근 20일 평균 대비 비율
- 업데이트 주기: 일간 종가 기준

---

### 2. Bollinger Bands

#### 개요
이동평균선을 중심으로 표준편차 기반 상/하한 밴드를 표시하는 지표

#### 계산 방식
```
Middle Band = 20일 단순이동평균 (SMA)
Upper Band = Middle Band + (2 × 20일 표준편차)
Lower Band = Middle Band - (2 × 20일 표준편차)

Band Width = Upper Band - Lower Band
```

#### 활용 방법
- **횡보/트렌드 판단**:
  - 밴드 폭 축소 → 횡보장 가능성
  - 밴드 폭 확대 → 트렌드 발생 가능성
- **진입 신호**: 밴드 폭이 최근 평균 이하로 수축 후 확장 시작 시점
- **청산 신호**: 가격이 밴드 상/하단 도달 시

#### 구현 요구사항
- 기본 설정: 20일 SMA, 2 표준편차
- 계산 결과: 상단/중단/하단 밴드 값, 밴드 폭, 최근 20일 평균 대비 비율
- 시각화: 차트 오버레이 옵션

---

### 3. Average Directional Index (ADX)

#### 개요
시장의 추세 강도를 측정하는 지표 (방향성은 제외)

#### 계산 방식
```
1. +DM = High(today) - High(yesterday) if positive, else 0
2. -DM = Low(yesterday) - Low(today) if positive, else 0
3. +DI = 100 × Smoothed +DM / ATR
4. -DI = 100 × Smoothed -DM / ATR
5. DX = 100 × |+DI - -DI| / (+DI + -DI)
6. ADX = Moving Average of DX (일반적으로 14일)
```

#### 활용 방법
- **추세/횡보 판단**:
  - ADX < 20: 횡보장 (추세 없음)
  - ADX 20~25: 약한 추세
  - ADX 25~50: 강한 추세
  - ADX > 50: 매우 강한 추세
- **전략 선택**:
  - ADX < 20: 추세추종 전략 보류, 범위매매 고려
  - ADX > 25: 추세추종 전략 진입 허용

#### 구현 요구사항
- 기본 기간: 14일
- 계산 결과: ADX 값, +DI, -DI
- 임계값 설정: 사용자 정의 가능 (기본값: 20, 25)

---

### 4. CBOE Volatility Index (VIX)

#### 개요
S&P 500 옵션 기반 향후 30일 기대 변동성 지수 ("공포 지수")

#### 데이터 소스
- CBOE 공식 데이터 (Yahoo Finance, Alpha Vantage 등 API 활용)
- 실시간 또는 일간 종가 기준

#### 활용 방법
- **시장 리스크 수준 판단**:
  - VIX < 15: 낮은 변동성 (안정적 시장)
  - VIX 15~20: 보통 변동성
  - VIX 20~30: 높은 변동성 (주의)
  - VIX > 30: 극도로 높은 변동성 (공포)
- **리스크 관리**: VIX 일정 수준 이상 시 포지션 축소 또는 진입 보류

#### 구현 요구사항
- 데이터 수집: 일간 종가 기준
- 계산 결과: 현재 VIX 값, 최근 20일 평균, 변화율
- 알림 설정: 임계값 초과 시 알림

---

### 5. 표준편차 (Standard Deviation)

#### 개요
가격 변화량의 통계적 분산을 측정하는 기본 변동성 지표

#### 계산 방식
```
1. 수익률 계산: Returns = (Close[i] - Close[i-1]) / Close[i-1]
2. 평균 수익률: Mean = Average(Returns)
3. 표준편차: StdDev = √(Σ(Returns - Mean)² / N)

연환산 변동성 = StdDev × √252 (거래일 기준)
```

#### 활용 방법
- **변동성 측정**: 절대적 변동성 수준 파악
- **리스크 조정 수익률**: Sharpe Ratio 계산 시 활용
- **포지션 사이징**: 표준편차 기반 리스크 한도 설정

#### 구현 요구사항
- 기본 기간: 20일 (사용자 설정 가능)
- 계산 결과: 일간 표준편차, 연환산 변동성
- 롤링 윈도우: 지정 기간 동안 이동 계산

---

## 🏗️ System Architecture

### 시장 상태 분류 체계

#### 1. 트렌드 유형 (Trend Type)
- **상승 추세 (Uptrend)**:
  - 조건: 가격 > 20일 SMA AND +DI > -DI AND ADX > 25
- **하락 추세 (Downtrend)**:
  - 조건: 가격 < 20일 SMA AND -DI > +DI AND ADX > 25
- **횡보장 (Range-bound)**:
  - 조건: ADX < 20 OR Bollinger Band Width < 평균 × 0.8

#### 2. 변동성 수준 (Volatility Level)
- **낮음 (Low)**:
  - ATR < 평균 × 0.8 AND Band Width < 평균 × 0.8
- **보통 (Normal)**:
  - 평균 × 0.8 ≤ ATR ≤ 평균 × 1.5 AND Band Width in normal range
- **높음 (High)**:
  - ATR > 평균 × 1.5 OR Band Width > 평균 × 1.5
- **극도로 높음 (Extreme)**:
  - ATR > 평균 × 2.0 OR VIX > 30

#### 3. 시장 리스크 상태 (Market Risk)
- **안정 (Stable)**: VIX < 15
- **주의 (Caution)**: VIX 15~20
- **경계 (Alert)**: VIX 20~30
- **위험 (Danger)**: VIX > 30

### 시장 상태 조합 매트릭스

| 트렌드 유형 | 변동성 수준 | 권장 전략 | 포지션 사이징 |
|------------|------------|----------|-------------|
| Uptrend | Low | 추세추종 (보수적) | 기본 × 0.8 |
| Uptrend | Normal | 추세추종 (적극적) | 기본 × 1.0 |
| Uptrend | High | 추세추종 (신중) | 기본 × 0.6 |
| Uptrend | Extreme | 진입 보류 | 기본 × 0.3 |
| Downtrend | Low | 공매도/관망 | 기본 × 0.5 |
| Downtrend | Normal | 공매도/관망 | 기본 × 0.3 |
| Downtrend | High | 관망 | 진입 금지 |
| Downtrend | Extreme | 관망 | 진입 금지 |
| Range-bound | Low | 범위매매 | 기본 × 0.5 |
| Range-bound | Normal | 범위매매 | 기본 × 0.7 |
| Range-bound | High | 관망 | 진입 보류 |
| Range-bound | Extreme | 관망 | 진입 금지 |

---

## 💻 Functional Requirements

### FR-1: 지표 자동 계산
- **ID**: FR-1
- **Priority**: P0 (Critical)
- **Description**:
  - 일간 종가 데이터 기반으로 모든 기술적 지표 자동 계산
  - ATR, Bollinger Bands, ADX, VIX, 표준편차
- **Acceptance Criteria**:
  - [ ] 모든 지표가 수식 오류 없이 계산됨
  - [ ] 계산 결과가 검증된 소스(TradingView 등)와 일치
  - [ ] 최소 1년치 과거 데이터 지원

### FR-2: 시장 상태 자동 분류
- **ID**: FR-2
- **Priority**: P0 (Critical)
- **Description**:
  - 계산된 지표 기반으로 시장 상태 자동 라벨링
  - 트렌드 유형, 변동성 수준, 리스크 상태 결정
- **Acceptance Criteria**:
  - [ ] 각 거래일마다 시장 상태 라벨 자동 생성
  - [ ] 라벨 변경 시 알림 또는 강조 표시
  - [ ] 과거 데이터의 시장 상태 재분류 가능

### FR-3: 웹 대시보드 UI
- **ID**: FR-3
- **Priority**: P0 (Critical)
- **Description**:
  - 반응형 웹 인터페이스로 데스크톱/모바일 지원
  - 실시간 데이터 업데이트 및 시각화
- **Acceptance Criteria**:
  - [ ] 시장 상태 대시보드 (종목별 현황)
  - [ ] 지표 차트 및 시각화
  - [ ] 거래 기록 입력 및 관리 UI
  - [ ] 반응형 디자인 (모바일 최적화)

### FR-4: 진입/청산 규칙 제안
- **ID**: FR-4
- **Priority**: P1 (High)
- **Description**:
  - 시장 상태에 따른 권장 진입/청산 조건 제시
  - 포지션 사이징 권장 비율 계산
- **Acceptance Criteria**:
  - [ ] 시장 상태 조합별 권장 전략 표시
  - [ ] 포지션 사이징 자동 계산 (기본 금액 × 조정 비율)
  - [ ] 손절/익절 권장 가격 제시 (ATR 기반)

### FR-5: 과거 거래 성과 분석
- **ID**: FR-5
- **Priority**: P1 (High)
- **Description**:
  - 시장 상태별 수익률, 승률, R-배수 분석
  - 어떤 시장 상태에서 수익/손실이 발생했는지 시각화
- **Acceptance Criteria**:
  - [ ] 시장 상태별 성과 요약 테이블 생성
  - [ ] 트렌드 유형별, 변동성별 수익률 비교
  - [ ] 차트 또는 대시보드 형태로 시각화

### FR-6: 알림 및 경고 시스템
- **ID**: FR-6
- **Priority**: P2 (Medium)
- **Description**:
  - 중요 임계값 도달 시 알림
  - 시장 상태 급변 시 경고
- **Acceptance Criteria**:
  - [ ] VIX > 30 시 알림
  - [ ] ADX가 20 이하에서 25 이상으로 전환 시 알림
  - [ ] Bollinger Band 폭 급격 확대 시 알림

### FR-7: 데이터 시각화
- **ID**: FR-7
- **Priority**: P2 (Medium)
- **Description**:
  - 지표 및 시장 상태 차트 생성
  - 시계열 추세 시각화
- **Acceptance Criteria**:
  - [ ] 지표별 차트 자동 생성
  - [ ] 시장 상태 구간별 색상 구분
  - [ ] 대시보드 형태의 종합 뷰 제공

---

## 🎨 Web Application UI/UX Specification

### Page Structure

#### 1. Landing Page (비로그인)
- **Hero Section**: 서비스 소개 및 주요 기능
- **Features Section**: 핵심 기능 3가지 (지표 계산, 시장 상태 판단, 성과 분석)
- **Pricing Section**: 무료/유료 플랜 (향후 확장)
- **CTA**: 회원가입/로그인 버튼

#### 2. Authentication Pages
- **로그인**: 이메일/비밀번호 또는 OAuth (구글/애플)
- **회원가입**: 이메일, 비밀번호, 약관 동의
- **비밀번호 재설정**: 이메일 기반 복구

#### 3. Main Dashboard (`/dashboard`)
**Layout**:
- Top Navigation Bar (로고, 워치리스트, 거래기록, 설정, 로그아웃)
- Sidebar (종목 검색, 워치리스트)
- Main Content Area (대시보드 위젯)

**Widgets**:
1. **시장 개요** (Market Overview)
   - VIX 현재 값 및 리스크 수준
   - S&P 500, NASDAQ 지수 현황
   - 전체 시장 상태 요약

2. **워치리스트** (Watchlist)
   - 종목 목록 (티커, 현재가, 변동률)
   - 시장 상태 라벨 (색상 코딩)
   - 빠른 차트 미리보기

3. **오늘의 추천** (Today's Recommendations)
   - 진입 추천 종목 (트렌드 + 변동성 조건 충족)
   - 청산 고려 종목 (리스크 수준 증가)

4. **최근 거래** (Recent Trades)
   - 최근 5개 거래 기록
   - 수익/손실, R-배수 표시

#### 4. Symbol Detail Page (`/symbol/:ticker`)
**Sections**:
1. **Header**
   - 종목명, 티커, 현재가, 변동률
   - 시장 상태 배지 (Uptrend High Volatility 등)
   - 워치리스트 추가/제거 버튼

2. **Price Chart** (Interactive)
   - Candlestick 차트 (TradingView 스타일)
   - Bollinger Bands 오버레이
   - 시장 상태 구간 색상 표시
   - 기간 선택 (1W, 1M, 3M, 6M, 1Y, All)

3. **Technical Indicators**
   - ATR: 현재 값, 20일 평균 대비 비율, 추세 그래프
   - Bollinger Bands: 밴드 폭, 20일 평균 대비 비율
   - ADX: 현재 값, +DI, -DI, 추세 강도
   - 표준편차: 일간/연환산 변동성

4. **Market State Analysis**
   - 트렌드 유형: Uptrend/Downtrend/Range (아이콘)
   - 변동성 수준: Low/Normal/High/Extreme (색상)
   - 리스크 상태: Stable/Caution/Alert/Danger (색상)
   - 권장 전략 및 포지션 사이징 비율

5. **Action Panel**
   - 진입 추천 가격 (ATR 기반)
   - 손절 추천 가격
   - 익절 추천 가격 (R-배수)
   - "거래 기록하기" 버튼

#### 5. Trade Journal Page (`/trades`)
**Features**:
1. **거래 목록 테이블**
   - 컬럼: 날짜, 종목, 진입가, 청산가, 수익/손실, R-배수, 시장상태
   - 필터: 종목, 날짜 범위, 수익/손실, 시장 상태
   - 정렬: 날짜, 수익률, R-배수

2. **거래 입력 폼** (Modal)
   - 종목 선택
   - 진입 날짜/가격
   - 청산 날짜/가격
   - 포지션 크기
   - 메모 (선택사항)
   - 자동 계산: 수익/손실, R-배수, 진입 시점 시장 상태

3. **성과 분석 섹션**
   - 전체 수익률, 승률
   - 시장 상태별 수익률 차트 (막대 그래프)
   - 월별 수익률 히트맵

#### 6. Analysis Page (`/analysis`)
**Sections**:
1. **시장 상태별 성과**
   - 테이블: 트렌드 유형 × 변동성 수준 → 거래 수, 승률, 평균 R
   - 인사이트: "Uptrend + Normal Volatility에서 가장 높은 수익률"

2. **시계열 분석**
   - 누적 수익률 차트
   - 드로다운 차트
   - 월별 수익률 바 차트

3. **통계 요약**
   - 최대 낙폭 (MDD)
   - 샤프 비율
   - 평균 보유 기간
   - 최대 연속 승/패

#### 7. Settings Page (`/settings`)
**Tabs**:
1. **계정 설정**
   - 이메일, 비밀번호 변경
   - 계정 삭제

2. **지표 설정**
   - ATR 기간 (기본 14일)
   - Bollinger Bands 기간/표준편차 (기본 20일, 2σ)
   - ADX 기간 (기본 14일)
   - 임계값 커스터마이징 (ADX 20/25 등)

3. **알림 설정**
   - 이메일 알림 활성화/비활성화
   - 알림 조건 설정 (VIX > 30, ADX 전환 등)

4. **데이터 관리**
   - 거래 기록 CSV 내보내기
   - 데이터 동기화 상태

---

## 🌐 API Endpoints Specification

### Authentication Endpoints

#### POST `/api/v1/auth/register`
**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```
**Response**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2025-11-12T10:00:00Z",
  "access_token": "jwt_token"
}
```

#### POST `/api/v1/auth/login`
**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```
**Response**:
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST `/api/v1/auth/refresh`
**Headers**: `Authorization: Bearer {token}`
**Response**:
```json
{
  "access_token": "new_jwt_token"
}
```

### Market Data Endpoints

#### GET `/api/v1/market/overview`
**Headers**: `Authorization: Bearer {token}`
**Response**:
```json
{
  "vix": {
    "current": 18.5,
    "change": -1.2,
    "risk_level": "caution"
  },
  "sp500": {
    "current": 4500.0,
    "change_percent": 0.8
  },
  "market_sentiment": "positive"
}
```

#### GET `/api/v1/symbols/search?q={query}`
**Query Params**: `q` (검색어, 최소 1자)
**Response**:
```json
{
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "sector": "Technology",
      "market": "NASDAQ"
    }
  ]
}
```

#### GET `/api/v1/symbols/{symbol}`
**Path Params**: `symbol` (티커, 예: AAPL)
**Response**:
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "current_price": 175.50,
  "change_percent": 1.2,
  "market_state": {
    "trend_type": "uptrend",
    "volatility_level": "normal",
    "risk_level": "stable",
    "recommended_strategy": "trend_following",
    "position_sizing_ratio": 1.0
  },
  "indicators": {
    "atr": 3.5,
    "atr_ratio": 1.1,
    "bb_width": 8.2,
    "bb_width_ratio": 0.95,
    "adx": 28.5,
    "plus_di": 25.0,
    "minus_di": 18.0,
    "std_dev": 0.022
  },
  "recommendations": {
    "entry_price": 174.0,
    "stop_loss": 170.0,
    "take_profit": 182.0
  }
}
```

#### GET `/api/v1/symbols/{symbol}/history?period={period}`
**Path Params**: `symbol` (티커)
**Query Params**: `period` (1w, 1m, 3m, 6m, 1y, all)
**Response**:
```json
{
  "symbol": "AAPL",
  "period": "3m",
  "data": [
    {
      "date": "2025-08-12",
      "open": 170.0,
      "high": 175.0,
      "low": 169.0,
      "close": 174.0,
      "volume": 50000000,
      "indicators": {
        "atr": 3.5,
        "bb_upper": 180.0,
        "bb_middle": 175.0,
        "bb_lower": 170.0,
        "adx": 28.5
      },
      "market_state": "uptrend_normal"
    }
  ]
}
```

### Watchlist Endpoints

#### GET `/api/v1/watchlist`
**Headers**: `Authorization: Bearer {token}`
**Response**:
```json
{
  "watchlist": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "current_price": 175.50,
      "change_percent": 1.2,
      "market_state": "uptrend_normal",
      "added_at": "2025-11-10T10:00:00Z"
    }
  ]
}
```

#### POST `/api/v1/watchlist`
**Headers**: `Authorization: Bearer {token}`
**Request**:
```json
{
  "symbol": "AAPL"
}
```
**Response**:
```json
{
  "message": "Added to watchlist",
  "watchlist_id": "uuid"
}
```

#### DELETE `/api/v1/watchlist/{symbol}`
**Headers**: `Authorization: Bearer {token}`
**Response**:
```json
{
  "message": "Removed from watchlist"
}
```

### Trade Journal Endpoints

#### GET `/api/v1/trades?limit={limit}&offset={offset}&filter={filter}`
**Headers**: `Authorization: Bearer {token}`
**Query Params**:
- `limit` (기본 50)
- `offset` (페이지네이션)
- `filter` (symbol, date_from, date_to, market_state)

**Response**:
```json
{
  "trades": [
    {
      "id": "uuid",
      "symbol": "AAPL",
      "entry_date": "2025-11-01",
      "exit_date": "2025-11-05",
      "entry_price": 170.0,
      "exit_price": 180.0,
      "position_size": 10,
      "pnl": 100.0,
      "r_multiple": 2.5,
      "market_state": "uptrend_normal",
      "notes": "Good trend following setup"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

#### POST `/api/v1/trades`
**Headers**: `Authorization: Bearer {token}`
**Request**:
```json
{
  "symbol": "AAPL",
  "entry_date": "2025-11-01",
  "exit_date": "2025-11-05",
  "entry_price": 170.0,
  "exit_price": 180.0,
  "position_size": 10,
  "notes": "Good trend following setup"
}
```
**Response**:
```json
{
  "id": "uuid",
  "pnl": 100.0,
  "r_multiple": 2.5,
  "market_state": "uptrend_normal"
}
```

#### PUT `/api/v1/trades/{trade_id}`
**Headers**: `Authorization: Bearer {token}`
**Request**: 동일 (부분 업데이트 가능)

#### DELETE `/api/v1/trades/{trade_id}`
**Headers**: `Authorization: Bearer {token}`
**Response**:
```json
{
  "message": "Trade deleted"
}
```

### Analysis Endpoints

#### GET `/api/v1/analysis/performance`
**Headers**: `Authorization: Bearer {token}`
**Query Params**: `date_from`, `date_to` (선택사항)
**Response**:
```json
{
  "overall": {
    "total_trades": 150,
    "win_rate": 0.65,
    "total_pnl": 15000.0,
    "avg_r_multiple": 1.8,
    "max_drawdown": -2500.0,
    "sharpe_ratio": 1.5
  },
  "by_market_state": [
    {
      "trend_type": "uptrend",
      "volatility_level": "normal",
      "total_trades": 50,
      "win_rate": 0.75,
      "avg_pnl": 150.0,
      "avg_r_multiple": 2.2
    }
  ],
  "monthly": [
    {
      "month": "2025-11",
      "pnl": 2500.0,
      "trades": 15
    }
  ]
}
```

#### GET `/api/v1/analysis/market-state-breakdown`
**Headers**: `Authorization: Bearer {token}`
**Response**:
```json
{
  "matrix": [
    {
      "trend_type": "uptrend",
      "volatility_level": "normal",
      "trade_count": 50,
      "win_rate": 0.75,
      "avg_r": 2.2,
      "insight": "Best performance"
    }
  ]
}
```

### Data Update Endpoints

#### POST `/api/v1/data/update/{symbol}`
**Headers**: `Authorization: Bearer {token}`
**Path Params**: `symbol` (티커, 또는 `all`로 전체 업데이트)
**Response**:
```json
{
  "message": "Data update queued",
  "task_id": "uuid",
  "estimated_time": 30
}
```

#### GET `/api/v1/data/status/{task_id}`
**Headers**: `Authorization: Bearer {token}`
**Response**:
```json
{
  "task_id": "uuid",
  "status": "completed",
  "progress": 100,
  "message": "Data updated successfully"
}
```

### Settings Endpoints

#### GET `/api/v1/settings`
**Headers**: `Authorization: Bearer {token}`
**Response**:
```json
{
  "indicators": {
    "atr_period": 14,
    "bb_period": 20,
    "bb_std_dev": 2.0,
    "adx_period": 14,
    "adx_threshold_weak": 20,
    "adx_threshold_strong": 25
  },
  "notifications": {
    "email_enabled": true,
    "vix_threshold": 30,
    "adx_transition_alert": true
  }
}
```

#### PUT `/api/v1/settings`
**Headers**: `Authorization: Bearer {token}`
**Request**: 동일 구조 (부분 업데이트 가능)

---

## 🚀 Non-Functional Requirements

### NFR-1: 성능
- 1년치 데이터 (250 거래일) 계산 시간: < 5초
- 실시간 지표 업데이트: < 1초

### NFR-2: 정확성
- 지표 계산 오차율: < 0.1%
- TradingView, Yahoo Finance 등 검증된 소스와 비교

### NFR-3: 사용성
- 비프로그래머도 설정 및 사용 가능
- 명확한 사용자 가이드 및 예제 제공

### NFR-4: 확장성
- 최소 10개 종목 동시 추적 가능
- 향후 자동매매 시스템과 통합 가능한 구조

### NFR-5: 유지보수성
- 임계값 및 파라미터 사용자 정의 가능
- 수식 및 로직 명확하게 문서화

---

## 📊 Success Metrics

### 정량적 지표
1. **지표 정확도**: 검증 소스 대비 99% 이상 일치
2. **사용자 만족도**: 시장 상태 판단의 유용성 평가 (5점 만점 4점 이상)
3. **거래 성과 개선**: 시스템 도입 전후 3개월 수익률 비교
4. **의사결정 시간 단축**: 진입/청산 판단 시간 50% 이상 감소

### 정성적 지표
1. **감정적 거래 감소**: 규칙 기반 판단으로 충동적 거래 줄임
2. **일관성 향상**: 동일 조건에서 동일한 판단 내림
3. **학습 효과**: 과거 데이터 분석을 통한 개인 강점/약점 파악

---

## 🗓️ Implementation Roadmap

### Phase 1: MVP (4주)
**목표**: 기본 지표 계산 및 시장 상태 분류

- Week 1: ATR, 표준편차 계산 구현
- Week 2: Bollinger Bands, ADX 계산 구현
- Week 3: VIX 데이터 수집 및 통합
- Week 4: 시장 상태 분류 로직 구현 및 테스트

**Deliverables**:
- [ ] Google Sheets 템플릿 (지표 자동 계산)
- [ ] 시장 상태 라벨 자동 생성
- [ ] 사용자 가이드 초안

### Phase 2: 분석 기능 (3주)
**목표**: 과거 거래 성과 분석 및 시각화

- Week 5: 시장 상태별 수익률 분석 기능
- Week 6: 차트 및 대시보드 구현
- Week 7: 포지션 사이징 권장 기능

**Deliverables**:
- [ ] 성과 분석 대시보드
- [ ] 시장 상태별 전략 가이드
- [ ] 백테스트 결과 리포트

### Phase 3: 고급 기능 (3주)
**목표**: 알림, 자동화, 통합

- Week 8: 알림 시스템 구현
- Week 9: API 연동 (데이터 자동 수집)
- Week 10: 최종 테스트 및 문서화

**Deliverables**:
- [ ] 알림 시스템
- [ ] 자동 데이터 업데이트
- [ ] 완성된 사용자 매뉴얼

### Phase 4: 검증 및 개선 (지속)
**목표**: 실전 적용 및 피드백 기반 개선

- 실제 거래 데이터로 3개월 검증
- 임계값 및 파라미터 최적화
- 사용자 피드백 반영

---

## 🛠️ Technical Stack (Railway.app 배포)

### Architecture Overview
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │────▶│   Database      │
│   (React +      │     │   (FastAPI +    │     │  (PostgreSQL)   │
│   TypeScript)   │     │    Python)      │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         │                       ▼                        │
         │              ┌─────────────────┐              │
         │              │  External APIs  │              │
         └──────────────│ Yahoo Finance   │──────────────┘
                        │ Alpha Vantage   │
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Railway.app    │
                        │   Deployment    │
                        └─────────────────┘
```

### Frontend Stack

#### Core Framework
- **React 18.3+**: UI 라이브러리
- **TypeScript 5.0+**: 타입 안정성
- **Vite**: 빌드 도구 (빠른 개발 서버)

#### UI/UX Libraries
- **Tailwind CSS 3.4+**: 유틸리티 기반 스타일링
- **shadcn/ui**: 재사용 가능한 컴포넌트 시스템
- **Recharts**: 차트 및 데이터 시각화
- **React Query (TanStack Query)**: 서버 상태 관리
- **Zustand**: 클라이언트 상태 관리

#### Additional Tools
- **React Router v6**: 라우팅
- **Axios**: HTTP 클라이언트
- **date-fns**: 날짜 처리
- **Zod**: 런타임 타입 검증

### Backend Stack

#### Core Framework
- **FastAPI 0.109+**: 고성능 비동기 API 프레임워크
- **Python 3.11+**: 프로그래밍 언어
- **Pydantic V2**: 데이터 검증 및 설정 관리

#### Data Processing
- **pandas 2.2+**: 시계열 데이터 처리
- **numpy 1.26+**: 수치 계산
- **ta-lib**: 기술적 지표 계산 (ATR, ADX, Bollinger Bands)
- **yfinance**: Yahoo Finance 데이터 수집

#### Database & ORM
- **PostgreSQL 16+**: 메인 데이터베이스
- **SQLAlchemy 2.0+**: ORM 및 데이터베이스 추상화
- **Alembic**: 데이터베이스 마이그레이션

#### Task Queue & Scheduling
- **Celery**: 비동기 작업 처리
- **Redis**: 메시지 브로커 및 캐싱
- **APScheduler**: 일간 데이터 업데이트 스케줄링

#### API Integration
- **httpx**: 비동기 HTTP 클라이언트
- **aiohttp**: 비동기 API 호출
- **python-dotenv**: 환경 변수 관리

### Database Schema

#### Tables Structure
```sql
-- 사용자 관리
users (
  id: UUID PRIMARY KEY,
  email: VARCHAR UNIQUE,
  hashed_password: VARCHAR,
  created_at: TIMESTAMP,
  is_active: BOOLEAN
)

-- 종목 관리
symbols (
  id: SERIAL PRIMARY KEY,
  symbol: VARCHAR UNIQUE,
  name: VARCHAR,
  sector: VARCHAR,
  market: VARCHAR
)

-- 일간 가격 데이터
daily_prices (
  id: SERIAL PRIMARY KEY,
  symbol_id: INTEGER REFERENCES symbols(id),
  date: DATE,
  open: DECIMAL,
  high: DECIMAL,
  low: DECIMAL,
  close: DECIMAL,
  volume: BIGINT,
  UNIQUE(symbol_id, date)
)

-- 기술적 지표
technical_indicators (
  id: SERIAL PRIMARY KEY,
  symbol_id: INTEGER REFERENCES symbols(id),
  date: DATE,
  atr: DECIMAL,
  atr_ratio: DECIMAL,
  bb_upper: DECIMAL,
  bb_middle: DECIMAL,
  bb_lower: DECIMAL,
  bb_width: DECIMAL,
  bb_width_ratio: DECIMAL,
  adx: DECIMAL,
  plus_di: DECIMAL,
  minus_di: DECIMAL,
  vix: DECIMAL,
  std_dev: DECIMAL,
  UNIQUE(symbol_id, date)
)

-- 시장 상태
market_states (
  id: SERIAL PRIMARY KEY,
  symbol_id: INTEGER REFERENCES symbols(id),
  date: DATE,
  trend_type: VARCHAR, -- 'uptrend', 'downtrend', 'range'
  volatility_level: VARCHAR, -- 'low', 'normal', 'high', 'extreme'
  risk_level: VARCHAR, -- 'stable', 'caution', 'alert', 'danger'
  recommended_strategy: VARCHAR,
  position_sizing_ratio: DECIMAL,
  UNIQUE(symbol_id, date)
)

-- 사용자 거래 기록
trades (
  id: SERIAL PRIMARY KEY,
  user_id: UUID REFERENCES users(id),
  symbol_id: INTEGER REFERENCES symbols(id),
  entry_date: DATE,
  exit_date: DATE,
  entry_price: DECIMAL,
  exit_price: DECIMAL,
  position_size: DECIMAL,
  pnl: DECIMAL,
  market_state_id: INTEGER REFERENCES market_states(id),
  notes: TEXT
)

-- 사용자 워치리스트
watchlists (
  id: SERIAL PRIMARY KEY,
  user_id: UUID REFERENCES users(id),
  symbol_id: INTEGER REFERENCES symbols(id),
  created_at: TIMESTAMP,
  UNIQUE(user_id, symbol_id)
)
```

### Infrastructure (Railway.app)

#### Deployment Configuration
```toml
# railway.toml
[build]
  builder = "NIXPACKS"
  buildCommand = "npm run build && pip install -r requirements.txt"

[deploy]
  startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  healthcheckPath = "/health"
  healthcheckTimeout = 30
  restartPolicyType = "ON_FAILURE"
  restartPolicyMaxRetries = 3

[env]
  NODE_ENV = "production"
  PYTHON_VERSION = "3.11"
```

#### Services on Railway
1. **Web Service** (FastAPI Backend)
   - Environment: Python 3.11
   - Port: 8000
   - Health Check: `/health`

2. **PostgreSQL Database**
   - Version: 16
   - Managed by Railway
   - Auto-backups enabled

3. **Redis**
   - Used for Celery broker and caching
   - Managed by Railway

#### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...

# API Keys
YAHOO_FINANCE_API_KEY=...
ALPHA_VANTAGE_API_KEY=...

# JWT
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://yourdomain.com
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          pip install -r requirements.txt
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up
```

### Security & Authentication

#### Authentication Strategy
- **JWT (JSON Web Tokens)**: 토큰 기반 인증
- **bcrypt**: 비밀번호 해싱
- **OAuth2**: 향후 구글/애플 로그인 지원

#### Security Measures
- **HTTPS Only**: Railway의 자동 SSL/TLS
- **CORS Configuration**: 허용된 도메인만 접근
- **Rate Limiting**: API 호출 제한 (10 req/min per user)
- **SQL Injection Prevention**: SQLAlchemy ORM 사용
- **Input Validation**: Pydantic 모델 검증

### Performance Optimization

#### Caching Strategy
- **Redis**: API 응답 캐싱 (5분 TTL)
- **Database Indexing**: symbol_id, date, user_id
- **Query Optimization**: SELECT 최적화, N+1 방지

#### Monitoring & Logging
- **Railway Logs**: 실시간 로그 모니터링
- **Sentry**: 에러 트래킹 (선택사항)
- **Custom Metrics**: API 응답 시간, 데이터 업데이트 빈도

### Cost Estimation (Railway.app)

#### Free Tier
- $5 credit/month
- 적합: 개발 및 테스트

#### Hobby Plan ($5/month)
- Unlimited usage
- Custom domain
- Priority support
- **권장**: 개인 사용

#### Pro Plan ($20/month)
- Team collaboration
- Advanced analytics
- **권장**: 다수 사용자 서비스

### Development Environment

#### Local Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

#### Docker Compose (선택사항)
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: market_analysis
      POSTGRES_PASSWORD: password

  redis:
    image: redis:7-alpine
```

---

## 📚 References & Resources

### 학습 자료
1. **책**:
   - "Technical Analysis of the Financial Markets" - John Murphy
   - "Trading Systems and Methods" - Perry Kaufman
2. **온라인 코스**:
   - Investopedia: Technical Indicators Guide
   - TradingView: Pine Script Documentation

### 데이터 소스
1. **주가 데이터**:
   - Yahoo Finance API (무료)
   - Alpha Vantage (무료 + 유료)
   - IEX Cloud (유료)
2. **VIX 데이터**:
   - CBOE Official Data
   - Yahoo Finance (^VIX)
3. **백테스팅**:
   - QuantConnect (무료 + 유료)
   - Backtrader (Python 라이브러리)

### 검증 도구
1. **TradingView**: 지표 계산 결과 비교
2. **Thinkorswim**: 실시간 지표 검증
3. **Excel/Sheets**: 수동 계산 검증

---

## 🔒 Risk Mitigation

### 기술적 리스크
1. **데이터 품질**:
   - 리스크: 부정확한 데이터로 잘못된 판단
   - 대응: 복수 소스 크로스체크, 이상치 탐지
2. **계산 오류**:
   - 리스크: 지표 수식 구현 오류
   - 대응: 검증된 라이브러리 사용, 단위 테스트
3. **시스템 장애**:
   - 리스크: API 다운타임, 스프레드시트 오류
   - 대응: 로컬 백업, 대체 데이터 소스

### 운영 리스크
1. **과최적화 (Overfitting)**:
   - 리스크: 과거 데이터에만 맞는 임계값 설정
   - 대응: 아웃오브샘플 테스트, 보수적 파라미터
2. **시장 변화**:
   - 리스크: 시장 구조 변화로 지표 효과 감소
   - 대응: 정기적 백테스트, 파라미터 재조정
3. **사용자 오류**:
   - 리스크: 시스템 신호 무시 또는 잘못 해석
   - 대응: 명확한 가이드, 교육 자료

---

## 📞 Stakeholder Communication

### 주요 이해관계자
1. **사용자 (투자자)**: 시장 상태 판단 도구 사용
2. **개발자**: 시스템 구현 및 유지보수
3. **데이터 제공자**: API 연동 및 데이터 품질

### 커뮤니케이션 계획
- **주간 업데이트**: 개발 진행 상황, 이슈, 다음 단계
- **월간 리뷰**: 성과 지표, 사용자 피드백, 개선 사항
- **분기 평가**: 거래 성과 분석, 시스템 효과 검증

---

## ✅ Acceptance Criteria

### MVP 완료 기준 (Railway.app 배포)
1. [ ] 5가지 핵심 지표 (ATR, Bollinger Bands, ADX, VIX, 표준편차) 계산 정확도 99% 이상
2. [ ] 시장 상태 자동 분류 (트렌드 유형, 변동성 수준, 리스크 상태)
3. [ ] 반응형 웹 대시보드 (Desktop/Mobile)
4. [ ] 사용자 인증 시스템 (JWT 기반)
5. [ ] 최소 10개 종목 동시 추적 가능
6. [ ] Railway.app 성공적 배포 및 HTTPS 접근

### 전체 시스템 완료 기준
1. [ ] 과거 거래 성과 분석 기능 (시장 상태별 수익률)
2. [ ] 실시간 알림 시스템 (이메일)
3. [ ] 자동 데이터 업데이트 (Celery + Redis 스케줄링)
4. [ ] 인터랙티브 차트 대시보드 (Recharts)
5. [ ] 거래 기록 CSV 내보내기
6. [ ] 3개월 실전 검증 완료 (거래 성과 개선 확인)
7. [ ] Railway.app Hobby Plan 안정 운영 (99% 업타임)

---

## 📝 Next Steps

### 즉시 실행 항목 (Railway.app 웹앱 개발)
1. [ ] Railway.app 계정 생성 및 프로젝트 초기화
2. [ ] GitHub 저장소 생성 (프론트엔드/백엔드 monorepo 또는 분리)
3. [ ] 데이터 소스 API 키 발급
   - [ ] Yahoo Finance API (yfinance 라이브러리)
   - [ ] Alpha Vantage API (백업)
4. [ ] 로컬 개발 환경 구축
   - [ ] React + Vite + TypeScript 프론트엔드 초기화
   - [ ] FastAPI + Python 백엔드 초기화
   - [ ] PostgreSQL 로컬 Docker 컨테이너
   - [ ] Redis 로컬 Docker 컨테이너
5. [ ] Railway.app에 PostgreSQL + Redis 서비스 생성
6. [ ] 데이터베이스 스키마 마이그레이션 (Alembic)
7. [ ] 기본 인증 시스템 구현 (회원가입/로그인)

### 의사결정 완료 항목 ✅
1. [✅] 구현 플랫폼: Railway.app 전용 웹 애플리케이션
2. [✅] 프론트엔드: React 18 + TypeScript + Tailwind CSS + shadcn/ui
3. [✅] 백엔드: FastAPI + Python 3.11 + PostgreSQL + Redis
4. [ ] 임계값 초기 설정 (ADX 20/25, ATR 배수 등) - Phase 1에서 설정
5. [ ] 백테스트 기간 및 검증 종목 선정 - 최소 1년, S&P 500 주요 종목
6. [ ] 알림 방식: 이메일 (SendGrid 또는 AWS SES)

---

## 🎓 Appendix

### A. 용어 정리
- **ATR (Average True Range)**: 평균 참 범위, 변동성 지표
- **Bollinger Bands**: 볼린저 밴드, 가격 변동 범위 지표
- **ADX (Average Directional Index)**: 평균 방향성 지수, 추세 강도 지표
- **VIX (Volatility Index)**: 변동성 지수, 시장 공포 지표
- **표준편차 (Standard Deviation)**: 가격 변동의 통계적 분산

### B. 수식 참조
상세 수식 및 구현 코드는 별도 기술 문서 참조

### C. 예시 스프레드시트 구조
```
| 날짜 | 종목 | 종가 | ATR | Band Width | ADX | VIX | 시장상태 | 변동성 | 리스크 | 추천전략 | 포지션크기 |
```

### D. 백테스트 결과 템플릿
- 전체 기간 수익률
- 시장 상태별 수익률
- 최대 낙폭 (MDD)
- 샤프 비율
- 승률 및 평균 R-배수

---

**문서 승인**:
- [ ] 사용자 (투자자) 리뷰 및 승인
- [ ] 기술 팀 리뷰 및 실행 가능성 확인
- [ ] 최종 승인 및 개발 착수

**Version History**:
- v1.0 (2025-11-12): 초안 작성
- v2.0 (2025-11-12): Railway.app 배포를 위한 전용 웹앱 아키텍처로 전환
  - React + TypeScript + Tailwind CSS 프론트엔드
  - FastAPI + Python 백엔드
  - PostgreSQL 데이터베이스
  - 완전한 UI/UX 명세 추가
  - RESTful API 엔드포인트 전체 정의
  - Railway.app CI/CD 파이프라인 설계
