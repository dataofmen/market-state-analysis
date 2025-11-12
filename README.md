# Market State Analysis System

미국 주식 시장의 상태를 5가지 기술적 지표로 분석하여 최적의 투자 전략을 제시하는 웹 애플리케이션

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/7N2KpL?referralCode=dataofmen)

## 🚀 Quick Deploy

Railway에서 원클릭으로 배포하세요:
1. 위의 "Deploy on Railway" 버튼 클릭
2. GitHub 계정으로 로그인
3. 환경 변수 설정 (FMP_API_KEY, SECRET_KEY)
4. 자동 배포 시작!

## 📋 개요

시장의 추세, 변동성, 위험도를 실시간으로 분석하고 현재 시장 상태에 맞는 맞춤형 투자 전략을 제공합니다.

### 핵심 기능

- **하이브리드 매매 시그널 (Piotroski F-Score + 기술적 분석)**
  - Piotroski F-Score: 재무 건전성 평가 (9점 만점)
  - 기술적 지표: RSI, ADX, SMA, Golden/Death Cross, 볼륨 분석
  - 시그널 타입: STRONG_BUY, BUY, HOLD, WARNING, SELL, STRONG_SELL
  - 시그널 강도: VERY_STRONG, STRONG, MODERATE, WEAK

- **다중 타임프레임 분석 (Multi-Timeframe Analysis)** 🆕
  - 3개 타임프레임 동시 분석: 단기(20일), 중기(100일), 장기(200일)
  - 타임프레임 정렬 감지: ALIGNED (완전 정렬), PARTIAL_ALIGNED (부분 정렬), CONFLICTED (충돌)
  - 상위 타임프레임 우선: 장기 > 중기 > 단기 추세 방향
  - 거래 적합성 평가: 신뢰도 점수 (0-100%) 제공
  - 진입점 최적화: 하위 타임프레임으로 더 나은 진입가 찾기
  - 충돌 시 거래 회피: 타임프레임 충돌 시 WARNING 시그널 발생

- **5가지 기술적 지표 분석**
  - ATR (Average True Range): 변동성 측정
  - Bollinger Bands: 추세/횡보 구분
  - ADX (Average Directional Index): 추세 강도
  - VIX (Volatility Index): 시장 위험도
  - Standard Deviation: 통계적 변동성

- **시장 상태 분류**
  - 추세 유형: 상승/하락/횡보
  - 변동성: 낮음/보통/높음/극심
  - 위험도: 안정/주의/경고/위험

- **맞춤형 투자 전략**
  - 12가지 시장 상태별 최적화된 전략
  - 자동 포지션 크기 조절
  - 실시간 전략 추천
  - 목표가/손절가 자동 계산

## 🏗️ 기술 스택

### Frontend
- React 18.3+ with TypeScript 5.0+
- Vite (빌드 도구)
- Tailwind CSS 3.4+ (스타일링)
- shadcn/ui (컴포넌트 시스템)
- React Query (서버 상태 관리)
- Zustand (클라이언트 상태 관리)
- Recharts (데이터 시각화)

### Backend
- FastAPI 0.109+ with Python 3.11+
- PostgreSQL 16+ (데이터베이스)
- Redis (캐싱 & 메시지 브로커)
- SQLAlchemy 2.0+ (ORM)
- pandas 2.2+ (데이터 처리)
- TA-Lib (기술적 지표 계산)
- Celery (비동기 작업)

### Infrastructure
- Railway.app (배포 플랫폼)
- Docker & Docker Compose (로컬 개발)
- GitHub Actions (CI/CD)
- Financial Modeling Prep API (주식 데이터)

## 🚀 빠른 시작

### 사전 요구사항

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- FMP API Key

### 환경 변수 설정

```bash
# 백엔드 환경 변수
cp backend/.env.example backend/.env
# backend/.env 파일에 FMP_API_KEY와 SECRET_KEY 입력
```

### Docker로 실행

```bash
# 모든 서비스 시작 (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# 프론트엔드: http://localhost:3000
# 백엔드 API: http://localhost:8000
# API 문서: http://localhost:8000/docs
```

### 로컬 개발 환경

#### 백엔드

```bash
cd backend

# Python 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 개발 서버 시작
uvicorn app.main:app --reload
```

#### 프론트엔드

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm run dev
```

## 📁 프로젝트 구조

```
market-state-analysis-system/
├── frontend/                 # React 프론트엔드
│   ├── src/
│   │   ├── components/      # 재사용 가능한 컴포넌트
│   │   ├── pages/           # 페이지 컴포넌트
│   │   ├── hooks/           # 커스텀 훅
│   │   ├── lib/             # 유틸리티 함수
│   │   ├── types/           # TypeScript 타입 정의
│   │   └── styles/          # 스타일 파일
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── api/             # API 엔드포인트
│   │   ├── core/            # 핵심 설정
│   │   ├── models/          # 데이터베이스 모델
│   │   ├── schemas/         # Pydantic 스키마
│   │   ├── services/        # 비즈니스 로직
│   │   └── db/              # 데이터베이스 설정
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker/                   # Docker 설정
├── docs/                     # 문서
├── docker-compose.yml
├── railway.toml             # Railway.app 배포 설정
└── README.md
```

## 🔌 API 엔드포인트

### 인증
- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/login` - 로그인
- `POST /api/v1/auth/refresh` - 토큰 갱신

### 종목
- `GET /api/v1/symbols` - 종목 목록
- `GET /api/v1/symbols/{symbol}` - 종목 상세
- `GET /api/v1/symbols/search` - 종목 검색

### 관심 종목
- `GET /api/v1/watchlist` - 관심 종목 목록
- `POST /api/v1/watchlist` - 관심 종목 추가
- `DELETE /api/v1/watchlist/{id}` - 관심 종목 제거

### 거래 기록
- `GET /api/v1/trades` - 거래 기록 목록
- `POST /api/v1/trades` - 거래 기록 추가
- `PUT /api/v1/trades/{id}` - 거래 기록 수정
- `DELETE /api/v1/trades/{id}` - 거래 기록 삭제

### 분석
- `GET /api/v1/analysis/history` - 분석 기록

### 데이터 업데이트
- `POST /api/v1/data/update` - 데이터 업데이트 트리거

### 설정
- `GET /api/v1/settings` - 설정 조회
- `PUT /api/v1/settings` - 설정 수정

API 문서: `http://localhost:8000/docs` (Swagger UI)

## 📊 데이터베이스 스키마

주요 테이블:
- `users` - 사용자 정보
- `symbols` - 종목 정보
- `watchlists` - 관심 종목
- `technical_indicators` - 기술적 지표
- `market_states` - 시장 상태
- `trades` - 거래 기록
- `analysis_history` - 분석 기록
- `data_update_logs` - 데이터 업데이트 로그

## 🚢 배포

### Railway.app 배포

1. Railway.app 계정 생성 및 프로젝트 생성
2. PostgreSQL과 Redis 서비스 추가
3. GitHub 저장소 연결
4. 환경 변수 설정:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `FMP_API_KEY`
   - `SECRET_KEY`
   - `ALLOWED_ORIGINS`

5. Railway.app이 자동으로 빌드 및 배포 진행

### 환경 변수

```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
FMP_API_KEY=your-fmp-api-key
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=https://yourdomain.com
```

## 📈 개발 로드맵

### Phase 1: MVP (4주)
- ✅ 프로젝트 초기화
- ⏳ 기본 지표 계산 시스템
- ⏳ 웹 대시보드 구현

### Phase 2: 거래 기록 (3주)
- ⏳ 거래 일지 기능
- ⏳ 성과 분석

### Phase 3: 알림 시스템 (3주)
- ⏳ 시장 상태 변화 알림
- ⏳ 자동 데이터 업데이트

### Phase 4: 실전 검증 (지속)
- ⏳ 성과 모니터링
- ⏳ 전략 최적화

## 🤝 기여

이 프로젝트에 기여하고 싶으신가요?

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이센스

This project is licensed under the MIT License.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 Issue를 생성해주세요.

## 🙏 감사의 글

- Financial Modeling Prep API for market data
- TA-Lib for technical indicators
- Railway.app for hosting platform
