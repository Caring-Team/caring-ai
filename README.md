# [Feature] AI 기반 기관 추천 시스템 구현

## 📋 이슈 개요
임베딩 벡터 기반 AI 추천 시스템을 구축하여 사용자의 요구사항과 기관의 특성을 매칭하고, **추천 이유를 행렬 계산으로 제공**합니다.

## 🎯 목적
- **개인화 추천**: 사용자 선호 태그와 어르신 프로필 기반 맞춤 추천
- **추천 이유 제공**: 왜 이 기관을 추천했는지 구체적 이유 제시
- **AI 서버 분리**: 확장 가능한 아키텍처 (FastAPI + Python)
- **실시간 처리**: 빠른 응답 속도 (< 1초)

---

## 📋 전체 API 엔드포인트 목록

### Part 1: 추천 API (Backend)

| Method | Endpoint | 설명 | 권한 | 상태 |
|--------|----------|------|------|------|
| POST | `/api/v1/recommendations` | 기관 추천 요청 | USER | ❌ 구현 필요 |
| GET | `/api/v1/recommendations/history` | 추천 이력 조회 | USER | ❌ 구현 필요 |
| POST | `/api/v1/recommendations/feedback` | 추천 피드백 | USER | ❌ 구현 필요 |

### Part 2: AI 서버 API (FastAPI)

| Method | Endpoint | 설명 | 권한 | 상태 |
|--------|----------|------|------|------|
| POST | `/api/v1/ai/embeddings/text` | 텍스트 임베딩 생성 | Internal | ❌ 구현 필요 |
| POST | `/api/v1/ai/embeddings/institution` | 기관 임베딩 생성 | Internal | ❌ 구현 필요 |
| POST | `/api/v1/ai/recommend` | 유사도 기반 추천 | Internal | ❌ 구현 필요 |
| POST | `/api/v1/ai/reasons` | 추천 이유 계산 | Internal | ❌ 구현 필요 |
| GET | `/api/v1/ai/health` | AI 서버 헬스 체크 | Internal | ❌ 구현 필요 |

### Part 3: 벡터 DB 작업 (pgvector)

| 작업 | 설명 | 상태 |
|------|------|------|
| 테이블 생성 | institution_embeddings 테이블 | ❌ 구현 필요 |
| 인덱스 생성 | IVFFlat 인덱스 (ANN 검색) | ❌ 구현 필요 |
| 초기 벡터 생성 | 전체 기관 임베딩 생성 및 저장 | ❌ 구현 필요 |

### 📊 통계

```
Backend API: 3개 (전체 필요)
AI Server API: 5개 (전체 필요)
Vector DB 작업: 3개 (전체 필요)
```

---

## ✅ 구현 우선순위

### 1순위 (핵심 기능)
1. pgvector 테이블 생성
2. AI 서버 기본 구조 (FastAPI)
3. 텍스트 임베딩 생성 API
4. 기관 임베딩 생성 및 저장
5. 유사도 기반 추천 API

### 2순위 (추천 이유)
6. 추천 이유 계산 (���렬 기반)
7. Backend 추천 API 통합
8. 추천 이력 저장

### 3순위 (부가 기능)
9. 추천 피드백
10. 하이브리드 점수 계산

---

## 🎨 추천 플로우

### 전체 구조
```
[사용자] ──텍스트 입력──> [임베딩 벡터 변환] ──유사도 계산──> [기관 추천]
   │                                                          │
   └──────────────────> [추천 이유 행렬 계산] <───────────────┘
```

### 상세 플로우

```
1. 사용자 입력
   ├─ 선호 태그: 치매 전문, 24시간 운영, 식사 제공
   ├─ 어르신 정보: 82세, 치매, 당뇨
   └─ 위치: 서울 강남구

2. 텍스트 → 임베딩 벡터 변환
   "82세 여성 치매, 당뇨 질환. 치매 전문, 24시간 운영, 식사 제공 원함"
   → [0.23, 0.45, ..., 0.12] (1024차원 벡터, bge-m3 모델)

3. 기관 임베딩 벡터 (미리 저장됨)
   기관 A: [0.21, 0.48, ..., 0.15] (치매 전문, 24시간 운영)
   기관 B: [0.10, 0.32, ..., 0.08] (일반 케어)

4. 유사도 계산 (Cosine Similarity)
   기관 A: 0.95 (매우 유사)
   기관 B: 0.62 (보통)

5. 최종 점수 계산 (하이브리드)
   - 유사도 (0.6) + 리뷰 (0.2) + 거리 (0.1) + 신뢰도 (0.1)
   
6. 추천 이유 계산 ✅ 핵심!
   - 추천된 기관의 태그를 행렬로 분석
   - 사용자 텍스트와 각 태그의 연관도 계산
   - Top 3 이유 추출
```

---

## 🗄️ Part 1: Vector DB 설정 (pgvector)

### 구현 필요 (❌)

**1. pgvector 설치**

```bash
# Mac
brew install pgvector

# Docker Compose
services:
  postgres:
    image: ankane/pgvector:latest
    environment:
      POSTGRES_DB: caring
      POSTGRES_USER: caring_user
      POSTGRES_PASSWORD: caring_password
    ports:
      - "5432:5432"
```

**2. 벡터 테이블 생성**

```sql
-- pgvector extension 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 기관 벡터 저장 테이블
CREATE TABLE institution_embeddings (
    id BIGSERIAL PRIMARY KEY,
    institution_id BIGINT NOT NULL UNIQUE,
    embedding vector(1024),  -- bge-m3 모델 (1024차원)
    metadata JSONB,  -- 기관 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT fk_institution 
        FOREIGN KEY (institution_id) 
        REFERENCES institution(id) 
        ON DELETE CASCADE
);

-- 벡터 유사도 검색용 인덱스 (IVFFlat)
CREATE INDEX ON institution_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- 일반 인덱스
CREATE INDEX idx_institution_id ON institution_embeddings(institution_id);
CREATE INDEX idx_metadata ON institution_embeddings USING GIN (metadata);
```

**3. 유사도 검색 쿼리 예시**

```sql
-- 코사인 유사도 기반 Top 10 검색
SELECT 
    institution_id,
    1 - (embedding <=> '[0.23, 0.45, ...]'::vector) AS similarity,
    metadata
FROM institution_embeddings
WHERE metadata->>'city' = '서울'  -- 메타데이터 필터
ORDER BY embedding <=> '[0.23, 0.45, ...]'::vector
LIMIT 10;
```

---

## 🤖 Part 2: AI 서버 구현 (FastAPI)

### 구현 필요 (❌)

**1. 프로젝트 구조**

```
ai-server/
├── main.py                    # FastAPI 앱
├── models/
│   ├── __init__.py
│   ├── request.py            # Request DTO
│   └── response.py           # Response DTO
├── services/
│   ├── __init__.py
│   ├── embedding_service.py  # 임베딩 생성
│   ├── vector_db_service.py  # pgvector 연동
│   └── recommendation_service.py  # 추천 로직
├── utils/
│   ├── __init__.py
│   └── similarity.py         # 유사도 계산
├── requirements.txt
├── Dockerfile
└── .env
```

**2. requirements.txt**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sentence-transformers==2.2.2
numpy==1.24.3
psycopg2-binary==2.9.9
pgvector==0.2.4
python-dotenv==1.0.0
pydantic==2.5.0
torch==2.1.0
```

**3. models/request.py**

```python
from pydantic import BaseModel
from typing import List, Optional

class TextEmbeddingRequest(BaseModel):
    text: str

class InstitutionEmbeddingRequest(BaseModel):
    institution_id: int
    name: str
    tags: List[str]
    address: str
    description: Optional[str] = None

class RecommendationRequest(BaseModel):
    user_text: str
    latitude: float
    longitude: float
    limit: int = 10
    city: Optional[str] = None

class ReasonRequest(BaseModel):
    user_embedding: List[float]
    institution_id: int
    institution_tags: List[str]
```

**4. models/response.py**

```python
from pydantic import BaseModel
from typing import List, Optional

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    dimension: int

class RecommendationItem(BaseModel):
    institution_id: int
    similarity_score: float
    reasons: Optional[List['ReasonItem']] = None

class ReasonItem(BaseModel):
    reason: str
    match_percentage: int

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    total: int
    processing_time_ms: float
```

**5. services/embedding_service.py**

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingService:
    def __init__(self):
        # bge-m3 모델 로드 (1024차원)
        self.model = SentenceTransformer('BAAI/bge-m3')
        print("✅ bge-m3 모델 로드 완료 (1024차원)")
    
    def encode_text(self, text: str) -> np.ndarray:
        """텍스트를 임베딩 벡터로 변환"""
        return self.model.encode(text, normalize_embeddings=True)
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """여러 텍스트를 배치로 변환"""
        return self.model.encode(texts, normalize_embeddings=True)
    
    def create_institution_text(self, name: str, tags: List[str], 
                               address: str, description: str = "") -> str:
        """기관 정보를 텍스트로 변환"""
        text = f"기관명: {name}\n"
        text += f"위치: {address}\n"
        text += f"서비스 및 특징: {', '.join(tags)}\n"
        if description:
            text += f"설명: {description}"
        return text
```

**6. services/vector_db_service.py**

```python
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np
from typing import List, Dict, Optional
import os
import json

class VectorDBService:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "caring"),
            user=os.getenv("DB_USER", "caring_user"),
            password=os.getenv("DB_PASSWORD", "caring_password"),
            port=os.getenv("DB_PORT", "5432")
        )
        register_vector(self.conn)
        print("✅ pgvector 연결 완료")
    
    def search(self, query_vector: np.ndarray, top_k: int = 10, 
               city: Optional[str] = None) -> List[Dict]:
        """코사인 유사도 기반 벡터 검색"""
        cursor = self.conn.cursor()
        
        query = """
            SELECT 
                institution_id,
                1 - (embedding <=> %s::vector) AS similarity,
                metadata
            FROM institution_embeddings
        """
        
        params = [query_vector.tolist()]
        
        if city:
            query += " WHERE metadata->>'city' = %s"
            params.append(city)
        
        query += """
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params.extend([query_vector.tolist(), top_k])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        
        return [
            {
                'institution_id': row[0],
                'similarity_score': float(row[1]),
                'metadata': row[2]
            }
            for row in results
        ]
    
    def upsert(self, institution_id: int, embedding: np.ndarray, 
               metadata: Dict):
        """벡터 저장/업데이트"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO institution_embeddings 
                (institution_id, embedding, metadata, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (institution_id) 
            DO UPDATE SET 
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
        """, (institution_id, embedding.tolist(), json.dumps(metadata)))
        
        self.conn.commit()
        cursor.close()
```

**7. services/recommendation_service.py**

```python
import time
from typing import List, Dict
import numpy as np
from .embedding_service import EmbeddingService
from .vector_db_service import VectorDBService

class RecommendationService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_db_service = VectorDBService()
    
    def get_recommendations(self, user_text: str, latitude: float,
                           longitude: float, limit: int, 
                           city: str = None) -> Dict:
        """기관 추천"""
        start_time = time.time()
        
        # 1. 사용자 텍스트 임베딩
        user_embedding = self.embedding_service.encode_text(user_text)
        
        # 2. 유사도 검색
        results = self.vector_db_service.search(
            user_embedding, 
            top_k=limit * 2,
            city=city
        )
        
        # 3. 결과 포맷팅
        recommendations = [
            {
                'institution_id': item['institution_id'],
                'similarity_score': item['similarity_score']
            }
            for item in results[:limit]
        ]
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            'recommendations': recommendations,
            'total': len(recommendations),
            'processing_time_ms': processing_time
        }
    
    def calculate_reasons(self, user_embedding: np.ndarray, 
                         institution_tags: List[str]) -> List[Dict]:
        """추천 이유 계산 (행렬 기반)"""
        
        # 1. 각 태그 임베딩
        tag_embeddings = self.embedding_service.encode_batch(institution_tags)
        
        # 2. 유사도 행렬 계산
        similarities = []
        for i, tag_emb in enumerate(tag_embeddings):
            score = self._cosine_similarity(user_embedding, tag_emb)
            similarities.append({
                'tag': institution_tags[i],
                'score': float(score)
            })
        
        # 3. Top 3 이유 추출
        top_reasons = sorted(similarities, key=lambda x: x['score'], reverse=True)[:3]
        
        return [
            {
                'reason': reason['tag'],
                'match_percentage': int(reason['score'] * 100)
            }
            for reason in top_reasons
        ]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """코사인 유사도 계산"""
        return float(np.dot(vec1, vec2) / 
                    (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
```

**8. main.py**

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.request import *
from models.response import *
from services.embedding_service import EmbeddingService
from services.vector_db_service import VectorDBService
from services.recommendation_service import RecommendationService
import numpy as np

app = FastAPI(title="Caring AI Recommendation Server")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
embedding_service = EmbeddingService()
vector_db_service = VectorDBService()
recommendation_service = RecommendationService()

@app.get("/api/v1/ai/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "model": "bge-m3", "dimension": 1024}

@app.post("/api/v1/ai/embeddings/text", response_model=EmbeddingResponse)
async def create_text_embedding(request: TextEmbeddingRequest):
    """텍스트 임베딩 생성"""
    try:
        embedding = embedding_service.encode_text(request.text)
        return EmbeddingResponse(
            embedding=embedding.tolist(),
            dimension=len(embedding)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/embeddings/institution")
async def create_institution_embedding(request: InstitutionEmbeddingRequest):
    """기관 임베딩 생성 및 저장"""
    try:
        # 텍스트 생성
        text = embedding_service.create_institution_text(
            request.name,
            request.tags,
            request.address,
            request.description or ""
        )
        
        # 임베딩 생성
        embedding = embedding_service.encode_text(text)
        
        # pgvector에 저장
        metadata = {
            'name': request.name,
            'tags': request.tags,
            'address': request.address
        }
        vector_db_service.upsert(request.institution_id, embedding, metadata)
        
        return {"status": "success", "institution_id": request.institution_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    """유사도 기반 추천"""
    try:
        result = recommendation_service.get_recommendations(
            request.user_text,
            request.latitude,
            request.longitude,
            request.limit,
            request.city
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/reasons")
async def calculate_reasons(request: ReasonRequest):
    """추천 이유 계산"""
    try:
        user_embedding = np.array(request.user_embedding)
        reasons = recommendation_service.calculate_reasons(
            user_embedding,
            request.institution_tags
        )
        return {"reasons": reasons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**9. Dockerfile**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 모델 미리 다운로드
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

# 앱 코드 복사
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**10. 실행**

```bash
# 로컬 실행
uvicorn main:app --reload --port 8000

# Docker 실행
docker build -t caring-ai-server .
docker run -d -p 8000:8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=caring \
  caring-ai-server
```

---

## 🔗 Part 3: Backend 통합

### 구현 필요 (❌)

**1. Entity 생성**

```java
// RecommendationLog.java
@Entity
@Table(name = "recommendation_log")
public class RecommendationLog extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id")
    private Member member;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "elderly_profile_id")
    private ElderlyProfile elderlyProfile;
    
    @Column(columnDefinition = "TEXT")
    private String requestData;  // JSON
    
    @Column(columnDefinition = "TEXT")
    private String recommendedInstitutions;  // JSON
    
    private LocalDateTime createdAt;
}

// RecommendationFeedback.java
@Entity
@Table(name = "recommendation_feedback")
public class RecommendationFeedback extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recommendation_log_id")
    private RecommendationLog recommendationLog;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "institution_id")
    private Institution institution;
    
    @Enumerated(EnumType.STRING)
    private FeedbackType feedbackType;  // LIKE, DISLIKE, VIEWED, RESERVED
    
    private LocalDateTime createdAt;
}
```

**2. AI 서버 Client**

```java
// AiServerClient.java
@Component
@RequiredArgsConstructor
public class AiServerClient {
    
    private final WebClient webClient;
    
    @Value("${ai.server.url}")
    private String aiServerUrl;
    
    public RecommendationResponse getRecommendations(
            String userText, 
            Double latitude,
            Double longitude,
            Integer limit,
            String city) {
        
        RecommendationRequest request = new RecommendationRequest(
            userText, latitude, longitude, limit, city
        );
        
        return webClient.post()
            .uri(aiServerUrl + "/api/v1/ai/recommend")
            .bodyValue(request)
            .retrieve()
            .bodyToMono(RecommendationResponse.class)
            .timeout(Duration.ofSeconds(3))
            .onErrorResume(e -> {
                log.error("AI 서버 호출 실패", e);
                return Mono.empty();
            })
            .block();
    }
    
    public List<ReasonItem> calculateReasons(
            List<Double> userEmbedding,
            Long institutionId,
            List<String> tags) {
        
        ReasonRequest request = new ReasonRequest(
            userEmbedding, institutionId, tags
        );
        
        return webClient.post()
            .uri(aiServerUrl + "/api/v1/ai/reasons")
            .bodyValue(request)
            .retrieve()
            .bodyToMono(ReasonResponse.class)
            .map(ReasonResponse::getReasons)
            .block();
    }
}
```

**3. RecommendationService**

```java
@Service
@RequiredArgsConstructor
public class RecommendationService {
    
    private final AiServerClient aiServerClient;
    private final MemberRepository memberRepository;
    private final ElderlyProfileRepository elderlyProfileRepository;
    private final InstitutionRepository institutionRepository;
    private final RecommendationLogRepository recommendationLogRepository;
    
    @Transactional
    public RecommendationResponseDto getRecommendations(
            Long memberId,
            Long elderlyProfileId,
            Integer limit) {
        
        // 1. 어르신 프로필 조회
        ElderlyProfile elderly = elderlyProfileRepository.findById(elderlyProfileId)
            .orElseThrow(() -> new BusinessException(ErrorCode.ELDERLY_PROFILE_NOT_FOUND));
        
        // 2. 회원 선호 태그 조회
        List<String> preferenceTags = getPreferenceTags(memberId);
        
        // 3. 사용자 텍스트 생성
        String userText = buildUserText(elderly, preferenceTags);
        
        // 4. AI 서버 호출
        RecommendationResponse aiResponse = aiServerClient.getRecommendations(
            userText,
            elderly.getLocation().getLatitude(),
            elderly.getLocation().getLongitude(),
            limit,
            elderly.getAddress().getCity()
        );
        
        // 5. 추천 로그 저장
        saveRecommendationLog(memberId, elderlyProfileId, aiResponse);
        
        // 6. 응답 생성
        return buildResponse(aiResponse);
    }
    
    private String buildUserText(ElderlyProfile elderly, List<String> preferenceTags) {
        StringBuilder text = new StringBuilder();
        
        // 어르신 정보
        text.append(String.format("%d세 %s, ", 
            calculateAge(elderly.getBirthDate()), 
            elderly.getGender()));
        
        // 건강 정보
        if (elderly.getSpecialNotes() != null) {
            text.append(elderly.getSpecialNotes());
        }
        
        // 선호 태그
        if (!preferenceTags.isEmpty()) {
            text.append(". 원하는 조건: ");
            text.append(String.join(", ", preferenceTags));
        }
        
        return text.toString();
    }
}
```

**4. RecommendationController**

```java
@RestController
@RequestMapping("/api/v1/recommendations")
@RequiredArgsConstructor
public class RecommendationController {
    
    private final RecommendationService recommendationService;
    
    @PostMapping
    public ResponseEntity<ApiResponse<RecommendationResponseDto>> recommend(
            @AuthenticationPrincipal MemberDetails memberDetails,
            @Valid @RequestBody RecommendationRequestDto request) {
        
        Long memberId = memberDetails.getId();
        
        RecommendationResponseDto response = recommendationService.getRecommendations(
            memberId,
            request.elderlyProfileId(),
            request.limit()
        );
        
        return ResponseEntity.ok(
            ApiResponse.success("추천 조회 성공", response)
        );
    }
}
```

---

## 📋 구현 순서

### Step 1: Vector DB 설정 (1일)
- [ ] pgvector 설치 및 extension 활성화
- [ ] institution_embeddings 테이블 생성
- [ ] IVFFlat 인덱스 생성
- [ ] 검색 쿼리 테스트

### Step 2: AI 서버 기본 구조 (2일)
- [ ] FastAPI 프로젝트 생성
- [ ] requirements.txt 작성
- [ ] 프로젝트 구조 설정
- [ ] bge-m3 모델 로드 테스트
- [ ] 헬스 체크 API

### Step 3: 임베딩 서비스 (2일)
- [ ] EmbeddingService 구현
- [ ] VectorDBService 구현 (pgvector 연동)
- [ ] 텍스트 임베딩 API
- [ ] 기관 임베딩 생성 및 저장 API

### Step 4: 초기 벡터 생성 (1일)
- [ ] 전체 기관 데이터 가져오기
- [ ] 배치로 임베딩 생성
- [ ] pgvector에 저장
- [ ] 검증

### Step 5: 추천 서비스 (2일)
- [ ] RecommendationService 구현
- [ ] 유사도 기반 추천 API
- [ ] 유사도 검색 테스트

### Step 6: 추천 이유 계산 (2일)
- [ ] 행렬 기반 이유 계산 로직
- [ ] 추천 이유 API
- [ ] Top 3 이유 추출

### Step 7: Backend 통합 (3일)
- [ ] RecommendationLog, RecommendationFeedback Entity
- [ ] AiServerClient 구현
- [ ] RecommendationService 구현
- [ ] RecommendationController 구현
- [ ] WebClient 설정

### Step 8: Docker 배포 (1일)
- [ ] Dockerfile 작성
- [ ] docker-compose.yml 수정 (AI 서버 추가)
- [ ] 통합 테스트

### Step 9: 테스트 및 최적화 (2일)
- [ ] 전체 플로우 테스트
- [ ] 응답 속도 측정 (< 1초 목표)
- [ ] 에러 처리 개선
- [ ] Swagger 문서화

**예상 기간: 16일 (약 3주)**

---

## 🚨 핵심 주의사항

1. **성능**
   - 임베딩 생성: < 100ms
   - 벡터 검색: < 200ms
   - 추천 이유 계산: < 200ms
   - 전체 응답: < 1초 목표

2. **AI 서버 분리**
   - Backend와 독립적으로 스케일링
   - 장애 시 Fallback 전략 필요
   - Circuit Breaker 패턴 적용

3. **벡터 DB**
   - pgvector는 10만 벡터까지 무리 없음
   - 그 이상은 Pinecone 고려
   - 인덱스 튜닝 (lists = sqrt(총 개수))

4. **추천 이유**
   - 각 기관 태그별로 유사도 계산
   - Top 3 이유만 반환
   - 매칭률 %로 표시

5. **로그**
   - 모든 추천 요청 로그 저장
   - 피드백 데이터 수집 (학습용)

---

## 💡 구현 팁

### 1. 초기 벡터 생성 스크립트

```python
# generate_all_embeddings.py
import requests
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-m3')

# Backend에서 전체 기관 가져오기
response = requests.get("http://localhost:8080/api/v1/admin/institutions/all")
institutions = response.json()

for inst in institutions:
    # AI 서버로 임베딩 생성 요청
    requests.post("http://localhost:8000/api/v1/ai/embeddings/institution", json={
        "institution_id": inst['id'],
        "name": inst['name'],
        "tags": [tag['name'] for tag in inst['tags']],
        "address": f"{inst['address']['city']} {inst['address']['district']}",
        "description": inst.get('description', '')
    })
    
print("✅ 전체 기관 임베딩 생성 완료!")
```

### 2. Fallback 전략

```java
public RecommendationResponseDto getRecommendations(...) {
    try {
        // AI 서버 호출
        return aiServerClient.getRecommendations(...);
    } catch (Exception e) {
        log.error("AI 서버 장애, Fallback 실행", e);
        // 거리 기반 검색으로 대체
        return getFallbackRecommendations(...);
    }
}
```

### 3. 하이브리드 점수 계산

```python
def calculate_hybrid_score(similarity, review_score, distance_score):
    return (similarity * 0.6) + (review_score * 0.2) + (distance_score * 0.2)
```

---

## 🎯 완료 기준

- [ ] pgvector 테이블 생성 및 인덱스 완료
- [ ] AI 서버 정상 실행 (헬스 체크 통과)
- [ ] 전체 기관 임베딩 생성 완료
- [ ] Backend에서 추천 API 호출 성공
- [ ] 추천 이유가 정상 반환됨
- [ ] 응답 속도 < 1초
- [ ] Swagger 테스트 완료
- [ ] Docker 배포 완료

---

## 📚 참고 자료

- bge-m3 모델: https://huggingface.co/BAAI/bge-m3
- pgvector 문서: https://github.com/pgvector/pgvector
- FastAPI 문서: https://fastapi.tiangolo.com/
- sentence-transformers: https://www.sbert.net/

