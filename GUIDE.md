# 🚀 AI 서버 실행 가이드

## 📦 설치 및 실행

### 1. Docker Compose로 전체 실행 (권장)

```bash
# 전체 시스템 시작 (PostgreSQL + AI Server)
docker-compose up -d

# 로그 확인
docker-compose logs -f ai-server

# 종료
docker-compose down
```

### 2. 로컬 개발 환경 실행

```bash
# 1. PostgreSQL + pgvector 실행
docker-compose up -d postgres

# 2. Python 환경 설정
cd ai-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 5. 서버 실행
python main.py
```

서버가 정상 실행되면: http://localhost:8000

## 🧪 테스트

### API 테스트
```bash
# 전체 API 테스트
python ai-server/scripts/test_api.py

# 개별 테스트 (curl)
curl http://localhost:8000/api/v1/ai/health
```

### 초기 데이터 생성
```bash
# Backend에서 기관 데이터를 가져와 임베딩 생성
python ai-server/scripts/generate_embeddings.py
```

## 📡 API 엔드포인트

### 1. 헬스 체크
```
GET /api/v1/ai/health
```

### 2. 텍스트 임베딩 생성
```
POST /api/v1/ai/embeddings/text
Content-Type: application/json

{
  "text": "당뇨병 관리와 운동 치료가 필요합니다"
}
```

### 3. 기관 임베딩 생성
```
POST /api/v1/ai/embeddings/institution
Content-Type: application/json

{
  "institution_id": 1,
  "name": "서울재활병원",
  "tags": ["재활치료", "물리치료", "운동치료"],
  "address": "서울특별시 강남구",
  "description": "전문 재활 서비스 제공"
}
```

### 4. 기관 추천 (핵심 기능)
```
POST /api/v1/ai/recommend
Content-Type: application/json

{
  "user_text": "고혈압과 당뇨가 있어 운동치료가 필요합니다",
  "latitude": 37.4979,
  "longitude": 127.0276,
  "limit": 10,
  "city": "서울"
}
```

### 5. 추천 이유 계산 (핵심 기능)
```
POST /api/v1/ai/reasons
Content-Type: application/json

{
  "user_embedding": [0.23, 0.45, ...],  // 1024차원
  "institution_id": 1,
  "institution_tags": ["재활치료", "물리치료", "운동치료"]
}
```

## 🔄 Backend 연동 플로우

### 시나리오 1: 기관 추천
```
1. User → Backend: 추천 요청 (사용자 정보)
2. Backend → AI Server: POST /api/v1/ai/recommend
   - user_text: 사용자 정보를 텍스트로 변환
   - latitude, longitude: 사용자 위치
3. AI Server: 임베딩 생성 + 유사도 검색
4. AI Server → Backend: 추천 기관 ID 목록 + 유사도 점수
5. Backend: 기관 상세 정보 조회 + 응답
```

### 시나리오 2: 추천 이유
```
1. Backend → AI Server: POST /api/v1/ai/reasons
   - user_embedding: 이전에 생성한 사용자 임베딩
   - institution_tags: 추천된 기관의 태그 목록
2. AI Server: 태그별 유사도 행렬 계산
3. AI Server → Backend: Top 3 이유 + 일치도
4. Backend: 프론트엔드에 전달
```

## 🏗️ 아키텍처

```
┌─────────────────┐
│   Frontend      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Backend       │
│  (Spring Boot)  │
└────┬────────┬───┘
     │        │
     │        ↓
     │   ┌─────────────────┐
     │   │   AI Server     │
     │   │   (FastAPI)     │
     │   └────┬───────┬────┘
     │        │       │
     ↓        ↓       ↓
┌─────────────────┐ ┌──────────────┐
│  PostgreSQL     │ │  bge-m3      │
│  + pgvector     │ │  (1024차원)  │
└─────────────────┘ └──────────────┘
```

## 🎯 성능 최적화

### 벡터 인덱스
- IVFFlat 인덱스 사용 (근사 검색)
- lists 파라미터: sqrt(데이터 수)
- 예: 10,000개 → lists=100

### 배치 처리
- 태그 임베딩은 배치로 처리
- 병렬 처리로 추천 이유 계산 속도 향상

### 캐싱 전략 (향후)
- 자주 사용되는 사용자 임베딩 캐싱
- Redis 활용 고려

## 🐛 트러블슈팅

### pgvector 연결 실패
```bash
# PostgreSQL이 실행 중인지 확인
docker ps | grep postgres

# 스키마가 적용되었는지 확인
docker exec -it caring-postgres psql -U caring_user -d caring -c "\d institution_embeddings"
```

### 모델 다운로드 느림
```bash
# 모델을 미리 다운로드
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

### 메모리 부족
- bge-m3 모델은 약 2GB RAM 필요
- Docker 메모리 설정 확인

## 📚 참고 자료

- [pgvector 공식 문서](https://github.com/pgvector/pgvector)
- [bge-m3 모델](https://huggingface.co/BAAI/bge-m3)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
