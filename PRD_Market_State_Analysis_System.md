# PRD: 시장 상태 판단 시스템
## Market State Analysis System for Trading

**문서 버전**: 1.0
**작성일**: 2025-11-12
**프로젝트 코드**: 7412-PRD

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
- 스프레드시트 기반 매매일지 사용자

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

### FR-3: 스프레드시트 통합
- **ID**: FR-3
- **Priority**: P0 (Critical)
- **Description**:
  - Google Sheets 또는 Excel에서 직접 사용 가능한 형태로 구현
  - 기존 매매일지와 통합
- **Acceptance Criteria**:
  - [ ] 각 거래 행에 시장 상태 컬럼 자동 추가
  - [ ] 지표 값 자동 업데이트 (일간 또는 실시간)
  - [ ] 사용자 정의 수식 및 매크로 지원

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

## 🛠️ Technical Stack Recommendations

### Option 1: Google Sheets 기반
- **장점**: 접근성, 협업, 클라우드 동기화
- **도구**: Google Apps Script, Google Finance API
- **적합 대상**: 비프로그래머, 빠른 프로토타입

### Option 2: Excel + Python
- **장점**: 고급 분석, 백테스팅, 확장성
- **도구**: Python (pandas, numpy, ta-lib), xlwings
- **적합 대상**: 프로그래밍 가능, 대량 데이터 분석

### Option 3: 전용 웹 애플리케이션
- **장점**: 최고의 UX, 실시간 처리, 모바일 지원
- **도구**: React/Vue (프론트), Python/Node (백엔드), PostgreSQL
- **적합 대상**: 장기 프로젝트, 다수 사용자

**권장**: Phase 1-2는 Google Sheets, Phase 3-4는 Python 통합

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

### MVP 완료 기준
1. [ ] 5가지 핵심 지표 (ATR, Bollinger Bands, ADX, VIX, 표준편차) 계산 정확도 99% 이상
2. [ ] 시장 상태 자동 분류 (트렌드 유형, 변동성 수준, 리스크 상태)
3. [ ] Google Sheets 템플릿 완성 (최소 1년치 데이터 지원)
4. [ ] 사용자 가이드 제공 (설치, 설정, 사용법)
5. [ ] 최소 10개 종목 동시 추적 가능

### 전체 시스템 완료 기준
1. [ ] 과거 거래 성과 분석 기능 (시장 상태별 수익률)
2. [ ] 실시간 알림 시스템
3. [ ] 자동 데이터 업데이트 (API 연동)
4. [ ] 대시보드 시각화
5. [ ] 3개월 실전 검증 완료 (거래 성과 개선 확인)

---

## 📝 Next Steps

### 즉시 실행 항목
1. [ ] 데이터 소스 선정 및 API 키 발급 (Yahoo Finance or Alpha Vantage)
2. [ ] Google Sheets 템플릿 초안 생성
3. [ ] ATR 및 표준편차 수식 구현 및 테스트
4. [ ] 과거 1년치 S&P 500 데이터 수집

### 의사결정 필요 항목
1. [ ] 구현 플랫폼 최종 선택 (Google Sheets vs Python vs 웹앱)
2. [ ] 임계값 초기 설정 (ADX 20/25, ATR 배수 등)
3. [ ] 백테스트 기간 및 검증 종목 선정
4. [ ] 알림 방식 선택 (이메일, Slack, 모바일 푸시)

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
