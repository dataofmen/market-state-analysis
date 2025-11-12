# 개발 가이드

## 개발 환경 설정

### 1. 필수 소프트웨어 설치

- **Node.js 20+**: https://nodejs.org/
- **Python 3.11+**: https://www.python.org/
- **Docker Desktop**: https://www.docker.com/products/docker-desktop
- **Git**: https://git-scm.com/

### 2. 저장소 클론

```bash
git clone <repository-url>
cd market-state-analysis-system
```

### 3. 환경 변수 설정

```bash
# 백엔드 환경 변수
cp backend/.env.example backend/.env
```

`.env` 파일 편집:
```bash
FMP_API_KEY=your-actual-api-key
SECRET_KEY=your-secret-key-generate-with-openssl
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/market_state_db
REDIS_URL=redis://localhost:6379/0
```

### 4. Docker로 데이터베이스 시작

```bash
docker-compose up -d postgres redis
```

### 5. 백엔드 개발 환경

```bash
cd backend

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션 (최초 1회)
alembic upgrade head

# 개발 서버 시작
uvicorn app.main:app --reload
```

백엔드 서버: http://localhost:8000
API 문서: http://localhost:8000/docs

### 6. 프론트엔드 개발 환경

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm run dev
```

프론트엔드 서버: http://localhost:3000

## 개발 워크플로우

### 1. 새로운 기능 개발

```bash
# 새 브랜치 생성
git checkout -b feature/your-feature-name

# 코드 작성...

# 커밋
git add .
git commit -m "feat: add your feature description"

# 푸시
git push origin feature/your-feature-name
```

### 2. 코드 스타일

#### 백엔드 (Python)
```bash
# 코드 포맷팅
black app/

# 린트 체크
flake8 app/

# 타입 체크
mypy app/
```

#### 프론트엔드 (TypeScript)
```bash
# 린트 체크
npm run lint

# 타입 체크
npm run type-check  # (구현 예정)
```

### 3. 테스트

#### 백엔드
```bash
cd backend
pytest
```

#### 프론트엔드
```bash
cd frontend
npm run test  # (구현 예정)
```

## 데이터베이스 마이그레이션

### 새로운 마이그레이션 생성

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
```

### 마이그레이션 적용

```bash
alembic upgrade head
```

### 마이그레이션 롤백

```bash
alembic downgrade -1
```

## API 개발

### 1. 새로운 엔드포인트 추가

```python
# backend/app/api/v1/endpoints/your_module.py
from fastapi import APIRouter, Depends
from app.schemas.your_schema import YourSchema

router = APIRouter()

@router.get("/")
async def list_items():
    return {"items": []}

@router.post("/")
async def create_item(item: YourSchema):
    return {"id": 1, **item.dict()}
```

### 2. 스키마 정의

```python
# backend/app/schemas/your_schema.py
from pydantic import BaseModel

class YourSchema(BaseModel):
    name: str
    description: str | None = None
```

### 3. 데이터베이스 모델

```python
# backend/app/models/your_model.py
from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

class YourModel(Base):
    __tablename__ = "your_table"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
```

## 프론트엔드 개발

### 1. 새로운 페이지 추가

```tsx
// frontend/src/pages/YourPage.tsx
export default function YourPage() {
  return (
    <div>
      <h1>Your Page</h1>
    </div>
  )
}
```

```tsx
// frontend/src/App.tsx에 라우트 추가
<Route path="/your-page" element={<YourPage />} />
```

### 2. API 호출

```tsx
// frontend/src/hooks/useYourData.ts
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

export function useYourData() {
  return useQuery({
    queryKey: ['your-data'],
    queryFn: async () => {
      const { data } = await axios.get('/api/v1/your-endpoint')
      return data
    },
  })
}
```

### 3. 컴포넌트 사용

```tsx
import { useYourData } from '@/hooks/useYourData'

export default function YourComponent() {
  const { data, isLoading } = useYourData()

  if (isLoading) return <div>Loading...</div>

  return <div>{JSON.stringify(data)}</div>
}
```

## 트러블슈팅

### 백엔드 서버가 시작되지 않을 때

1. PostgreSQL/Redis가 실행 중인지 확인
   ```bash
   docker-compose ps
   ```

2. 환경 변수 확인
   ```bash
   cat backend/.env
   ```

3. 데이터베이스 연결 확인
   ```bash
   psql postgresql://postgres:postgres@localhost:5432/market_state_db
   ```

### 프론트엔드 빌드 에러

1. node_modules 재설치
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. 캐시 클리어
   ```bash
   npm run clean  # (스크립트 추가 필요)
   ```

### 데이터베이스 마이그레이션 에러

1. 마이그레이션 상태 확인
   ```bash
   alembic current
   alembic history
   ```

2. 데이터베이스 리셋 (개발 환경)
   ```bash
   docker-compose down -v
   docker-compose up -d postgres redis
   alembic upgrade head
   ```

## 유용한 명령어

```bash
# 전체 프로젝트 개발 서버 시작
npm run dev

# Docker 전체 재시작
docker-compose down && docker-compose up -d

# 백엔드 로그 확인
docker-compose logs -f backend

# 데이터베이스 접속
docker exec -it market_state_postgres psql -U postgres -d market_state_db

# Redis 접속
docker exec -it market_state_redis redis-cli
```

## 참고 자료

- FastAPI 문서: https://fastapi.tiangolo.com/
- React 문서: https://react.dev/
- Vite 문서: https://vitejs.dev/
- Tailwind CSS: https://tailwindcss.com/
- SQLAlchemy 문서: https://docs.sqlalchemy.org/
- Financial Modeling Prep API: https://site.financialmodelingprep.com/developer/docs
