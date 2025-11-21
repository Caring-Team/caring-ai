# Caring AI 추천 시스템 아키텍처

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [데이터 흐름 설계](#데이터-흐름-설계)
3. [임베딩 관리 전략](#임베딩-관리-전략)
4. [API 설계](#api-설계)
5. [구현 가이드](#구현-가이드)

---

## 시스템 개요

### 핵심 구조
```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Spring Backend │ ◄─────► │   AI Server     │ ◄─────► │  PostgreSQL     │
│  (API Gateway)  │         │  (FastAPI)      │         │  + pgvector     │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
       │                            │                           │
       │                            │                           │
   사용자 요청                   임베딩 생성              기관 데이터 + 벡터
   기관 등록/수정                유사도 계산
```

### 엔티티 구조
- **사용자**: 보호자 (Guardian) + 어르신 (Senior)
- **기관**: 3가지 타입의 요양기관 (Institution)
  - 타입 1: 재활병원
  - 타입 2: 요양센터  
  - 타입 3: 복지관

---

## 데이터 흐름 설계

### ✅ 권장 방안: **AI 서버가 DB 직접 접근**

#### 이유
1. **데이터 일관성**: 같은 PostgreSQL DB를 사용하므로 중복 전송 불필요
2. **효율성**: ID만 전송하여 네트워크 부하 최소화
3. **보안**: 민감한 사용자 정보를 네트워크로 전송하지 않음
4. **유지보수**: 데이터 스키마 변경 시 AI 서버만 수정

#### 데이터 접근 방식
```
Spring → AI Server: { userId, seniorId, preferredRegion }
         ↓
AI Server → PostgreSQL: SELECT * FROM users WHERE id = userId
                       SELECT * FROM institutions WHERE ...
         ↓
AI Server: 임베딩 생성 + 유사도 계산
         ↓
Spring ← AI Server: { recommendations: [institutionId, score, reasons] }
```

---

## 임베딩 관리 전략

### 🎯 기관 임베딩: **사전 생성 및 저장**

#### 타이밍
1. **기관 최초 등록 시**: 임베딩 생성 → DB 저장
2. **기관 정보 수정 시**: 임베딩 재생성 → DB 업데이트
3. **주기적 배치**: 매일 자정, 변경사항 있는 기관만 재생성

#### 저장 구조
```sql
-- institutions 테이블
CREATE TABLE institutions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    type VARCHAR(50),  -- '재활병원', '요양센터', '복지관'
    address TEXT,
    description TEXT,
    services JSONB,  -- ['재활치료', '물리치료', ...]
    embedding vector(1024),  -- pgvector
    embedding_version INT DEFAULT 1,  -- 임베딩 버전 관리
    updated_at TIMESTAMP,
    created_at TIMESTAMP
);

-- 임베딩 인덱스 (빠른 유사도 검색)
CREATE INDEX ON institutions USING ivfflat (embedding vector_cosine_ops);
```

#### 임베딩 업데이트 전략

**방식 1: 동기 업데이트 (권장 - 단순함)**
```
기관 수정 API 호출
  ↓
Spring: DB 업데이트
  ↓
Spring → AI Server: POST /embeddings/update
  {
    "institutionId": 123,
    "updateType": "modified"
  }
  ↓
AI Server: DB에서 최신 데이터 조회 → 임베딩 생성 → DB 업데이트
```

**방식 2: 비동기 업데이트 (대량 처리에 유리)**
```
기관 수정 API 호출
  ↓
Spring: DB 업데이트 + 메시지 큐 전송 (Redis/RabbitMQ)
  ↓
AI Server: 큐 리스너가 메시지 수신 → 임베딩 생성 → DB 업데이트
```

**방식 3: 배치 업데이트 (실시간 불필요 시)**
```
매일 자정 또는 특정 시간
  ↓
AI Server: 
  SELECT * FROM institutions 
  WHERE updated_at > last_embedding_update
  ↓
변경된 기관들만 임베딩 재생성
```

#### 🎯 권장: **방식 1 (동기) + 방식 3 (배치) 병행**
- 중요한 수정: 즉시 업데이트 (동기)
- 사소한 수정: 배치로 일괄 처리
- `embedding_version` 필드로 버전 관리

---

### 🔄 사용자 임베딩: **실시간 생성**

#### 이유
1. 사용자 요구사항은 매번 다를 수 있음
2. 사전 저장할 필요 없음 (추천 요청 시마다 생성)
3. 보호자 + 어르신 정보 결합이 동적

#### 프로세스
```
사용자 추천 요청
  ↓
AI Server: 
  1. userId, seniorId로 DB 조회
  2. 사용자 정보를 자연어로 변환
     "보호자는 서울 강남구에 거주하며, 
      어르신은 당뇨병과 고혈압이 있으시고 
      재활치료와 물리치료가 필요합니다."
  3. 실시간 임베딩 생성
  4. 기관 임베딩과 유사도 계산
```

---

## API 설계

### 1️⃣ 기관 임베딩 생성/업데이트

**endpoint**: `POST /api/embeddings/institutions`

**요청 (Spring → AI)**
```json
{
  "institutionId": 123,
  "action": "create" | "update" | "delete"
}
```

**응답 (AI → Spring)**
```json
{
  "success": true,
  "institutionId": 123,
  "embeddingVersion": 2,
  "message": "임베딩이 성공적으로 업데이트되었습니다."
}
```

**AI 서버 처리**
```python
# 1. DB에서 기관 정보 조회
institution = db.query("SELECT * FROM institutions WHERE id = ?", institutionId)

# 2. 자연어 텍스트 변환
text = f"{institution.name}은 {', '.join(institution.services)}을 제공하는 기관입니다. "
text += f"{institution.description}. 위치는 {institution.address}입니다."

# 3. 임베딩 생성
embedding = model.encode(text, normalize_embeddings=True)

# 4. DB 업데이트
db.execute(
    "UPDATE institutions SET embedding = ?, embedding_version = embedding_version + 1 WHERE id = ?",
    embedding.tolist(), institutionId
)
```

---

### 2️⃣ 사용자 추천 요청 (핵심 API)

**endpoint**: `POST /api/recommendations`

**요청 (Spring → AI)**
```json
{
  "guardianId": 456,
  "seniorId": 789,
  "preferences": {
    "region": "서울특별시 강남구",
    "institutionTypes": ["재활병원", "요양센터"],  // null이면 전체
    "maxDistance": 10  // km, optional
  },
  "topK": 10  // 상위 몇 개 추천
}
```

**응답 (AI → Spring)**
```json
{
  "recommendations": [
    {
      "institutionId": 123,
      "institutionName": "서울재활병원",
      "institutionType": "재활병원",
      "score": 0.8542,  // 0~1 사이 유사도 점수
      "matchedReasons": [
        {
          "category": "질환관리",
          "keywords": ["당뇨병", "고혈압"],
          "relevance": 0.92
        },
        {
          "category": "치료서비스",
          "keywords": ["재활치료", "물리치료"],
          "relevance": 0.87
        }
      ],
      "distance": 3.2  // km
    },
    // ... 9개 더
  ],
  "metadata": {
    "totalCandidates": 50,
    "filteredByRegion": 25,
    "searchTime": 0.045  // seconds
  }
}
```

**AI 서버 처리 (상세)**
```python
@app.post("/api/recommendations")
async def get_recommendations(request: RecommendationRequest):
    # 1. 사용자 데이터 조회
    guardian = db.query(
        "SELECT * FROM guardians WHERE id = ?", 
        request.guardianId
    )
    senior = db.query(
        "SELECT * FROM seniors WHERE id = ?", 
        request.seniorId
    )
    
    # 2. 사용자 정보를 자연어로 변환
    user_text = create_user_query(guardian, senior)
    # 예: "보호자는 서울 강남구 거주, 어르신은 당뇨병과 고혈압이 있으며 
    #      재활치료와 물리치료가 필요합니다."
    
    # 3. 사용자 쿼리 임베딩 생성 (실시간)
    query_embedding = model.encode(
        f"질문: {user_text}", 
        normalize_embeddings=True
    )
    
    # 4. 벡터 유사도 검색 (pgvector)
    sql = """
        SELECT 
            id, name, type, address, services, description,
            1 - (embedding <=> %s::vector) as similarity
        FROM institutions
        WHERE type = ANY(%s)  -- 타입 필터
          AND region = %s     -- 지역 필터
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """
    
    candidates = db.query(
        sql, 
        query_embedding.tolist(),
        request.preferences.institutionTypes,
        request.preferences.region,
        query_embedding.tolist(),
        request.topK
    )
    
    # 5. 추천 이유 분석 (각 기관의 태그별 유사도)
    recommendations = []
    for candidate in candidates:
        reasons = analyze_match_reasons(
            query_embedding, 
            candidate.services,
            model
        )
        
        recommendations.append({
            "institutionId": candidate.id,
            "institutionName": candidate.name,
            "score": candidate.similarity,
            "matchedReasons": reasons
        })
    
    return recommendations
```

---

### 3️⃣ 배치 임베딩 업데이트

**endpoint**: `POST /api/embeddings/batch-update`

**요청 (Scheduler → AI)**
```json
{
  "mode": "modified_only" | "all",
  "since": "2024-01-01T00:00:00Z"  // modified_only 모드
}
```

**응답**
```json
{
  "success": true,
  "updated": 15,
  "failed": 0,
  "duration": 12.5  // seconds
}
```

---

## 구현 가이드

### Phase 1: 기본 구조 구축 ✅

#### 1.1 AI 서버에 DB 연결 추가
```python
# services/database_service.py
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseService:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
    
    def get_institution(self, institution_id: int):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM institutions WHERE id = %s",
                (institution_id,)
            )
            return cur.fetchone()
```

#### 1.2 텍스트 변환 유틸리티
```python
# utils/text_converter.py

def institution_to_text(institution: dict) -> str:
    """기관 정보를 자연어 passage로 변환"""
    services = ", ".join(institution['services'])
    text = f"{institution['name']}은 {services}을 제공하는 기관입니다. "
    text += f"{institution['description']}. "
    text += f"위치는 {institution['address']}입니다."
    return text

def user_to_query(guardian: dict, senior: dict) -> str:
    """사용자 정보를 자연어 query로 변환"""
    text = f"보호자는 {guardian['region']}에 거주하며, "
    
    # 어르신 건강 상태
    if senior['diseases']:
        diseases = ", ".join(senior['diseases'])
        text += f"어르신은 {diseases}가 있고 "
    
    # 필요한 서비스
    if senior['required_services']:
        services = ", ".join(senior['required_services'])
        text += f"{services}가 필요합니다."
    
    return text
```

---

### Phase 2: 임베딩 생성 API ✅

```python
# main.py

@app.post("/api/embeddings/institutions")
async def update_institution_embedding(request: InstitutionEmbeddingRequest):
    """기관 임베딩 생성/업데이트"""
    
    # 1. DB에서 기관 정보 조회
    institution = db_service.get_institution(request.institutionId)
    
    if not institution:
        raise HTTPException(404, "기관을 찾을 수 없습니다")
    
    # 2. 자연어 변환
    passage_text = text_converter.institution_to_text(institution)
    
    # 3. 임베딩 생성
    embedding = embedding_service.encode_passage(passage_text)
    
    # 4. DB 저장
    db_service.save_institution_embedding(
        institution_id=request.institutionId,
        embedding=embedding.tolist()
    )
    
    return {
        "success": True,
        "institutionId": request.institutionId,
        "embeddingVersion": institution['embedding_version'] + 1
    }
```

---

### Phase 3: 추천 API ✅

```python
@app.post("/api/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """사용자 맞춤 기관 추천"""
    
    # 1. 사용자 정보 조회
    guardian = db_service.get_guardian(request.guardianId)
    senior = db_service.get_senior(request.seniorId)
    
    # 2. 사용자 쿼리 생성
    query_text = text_converter.user_to_query(guardian, senior)
    
    # 3. 쿼리 임베딩 생성 (실시간)
    query_embedding = embedding_service.encode_query(query_text)
    
    # 4. 벡터 유사도 검색
    candidates = vector_db_service.search_similar_institutions(
        query_embedding=query_embedding,
        filters={
            "types": request.preferences.institutionTypes,
            "region": request.preferences.region
        },
        top_k=request.topK
    )
    
    # 5. 추천 이유 분석
    recommendations = recommendation_service.analyze_matches(
        query_embedding=query_embedding,
        candidates=candidates
    )
    
    return {
        "recommendations": recommendations,
        "metadata": {
            "totalCandidates": len(candidates),
            "searchTime": 0.045
        }
    }
```

---

### Phase 4: Spring 연동

#### 4.1 Spring에서 AI 서버 호출
```java
@Service
public class AIRecommendationService {
    
    @Value("${ai.server.url}")
    private String aiServerUrl;
    
    private final RestTemplate restTemplate;
    
    public List<InstitutionRecommendation> getRecommendations(
        Long guardianId, 
        Long seniorId,
        RecommendationPreferences preferences
    ) {
        // AI 서버로 요청
        RecommendationRequest request = RecommendationRequest.builder()
            .guardianId(guardianId)
            .seniorId(seniorId)
            .preferences(preferences)
            .topK(10)
            .build();
        
        RecommendationResponse response = restTemplate.postForObject(
            aiServerUrl + "/api/recommendations",
            request,
            RecommendationResponse.class
        );
        
        // 결과 처리
        return response.getRecommendations().stream()
            .map(this::enrichWithDetails)  // DB에서 추가 정보 조회
            .collect(Collectors.toList());
    }
}
```

#### 4.2 기관 수정 시 임베딩 업데이트
```java
@Service
public class InstitutionService {
    
    @Autowired
    private AIEmbeddingService aiEmbeddingService;
    
    @Transactional
    public Institution updateInstitution(Long id, InstitutionUpdateDto dto) {
        // 1. DB 업데이트
        Institution institution = institutionRepository.findById(id)
            .orElseThrow();
        institution.update(dto);
        institutionRepository.save(institution);
        
        // 2. AI 서버에 임베딩 업데이트 요청 (비동기)
        CompletableFuture.runAsync(() -> {
            aiEmbeddingService.updateEmbedding(id);
        });
        
        return institution;
    }
}
```

---

## 데이터 변환 예시

### 기관 데이터 → 자연어 Passage
```
입력 (DB):
{
  "id": 123,
  "name": "서울재활병원",
  "type": "재활병원",
  "address": "서울특별시 강남구 테헤란로 123",
  "services": ["재활치료", "물리치료", "운동치료", "당뇨관리"],
  "description": "전문 재활 서비스를 제공하는 종합 의료 기관"
}

출력 (자연어):
"서울재활병원은 재활치료, 물리치료, 운동치료, 당뇨관리를 제공하는 기관입니다. 
전문 재활 서비스를 제공하는 종합 의료 기관. 
위치는 서울특별시 강남구 테헤란로 123입니다."
```

### 사용자 데이터 → 자연어 Query
```
입력 (DB):
Guardian: {
  "id": 456,
  "region": "서울특별시 강남구"
}
Senior: {
  "id": 789,
  "diseases": ["당뇨병", "고혈압"],
  "required_services": ["재활치료", "물리치료"]
}

출력 (자연어):
"질문: 보호자는 서울특별시 강남구에 거주하며, 
어르신은 당뇨병, 고혈압가 있고 재활치료, 물리치료가 필요합니다."
```

---

## 성능 최적화

### 1. 벡터 인덱스 생성
```sql
-- IVFFlat 인덱스 (빠른 근사 검색)
CREATE INDEX institutions_embedding_idx 
ON institutions 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- HNSW 인덱스 (더 빠르지만 메모리 많이 사용)
CREATE INDEX institutions_embedding_hnsw_idx 
ON institutions 
USING hnsw (embedding vector_cosine_ops);
```

### 2. 캐싱 전략
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_institution_embedding(institution_id: int):
    """자주 조회되는 기관 임베딩 캐싱"""
    return db_service.get_institution_embedding(institution_id)
```

### 3. 배치 임베딩 생성
```python
# 한 번에 여러 기관 임베딩 생성 (GPU 효율)
texts = [institution_to_text(inst) for inst in institutions]
embeddings = model.encode(texts, batch_size=32)
```

---

## 체크리스트

### AI 서버 구현
- [ ] PostgreSQL 연결 설정
- [ ] 기관 데이터 조회 서비스
- [ ] 사용자 데이터 조회 서비스
- [ ] 텍스트 변환 유틸리티
- [ ] 임베딩 생성 API
- [ ] 추천 API
- [ ] 배치 업데이트 스크립트

### Spring 백엔드 구현
- [ ] AI 서버 호출 서비스
- [ ] 기관 수정 시 임베딩 업데이트 트리거
- [ ] 추천 결과 처리 로직
- [ ] 에러 핸들링

### 데이터베이스
- [ ] institutions 테이블에 embedding 컬럼 추가
- [ ] pgvector 익스텐션 설치
- [ ] 벡터 인덱스 생성
- [ ] 기존 기관 데이터 임베딩 생성

### 테스트
- [ ] 임베딩 생성 테스트
- [ ] 유사도 검색 테스트
- [ ] 추천 정확도 검증
- [ ] 성능 테스트 (응답 시간 < 100ms)

---

## 다음 단계

1. ✅ **임베딩 기본 검증 완료** (test_embedding_similarity.py)
2. 🔄 **벡터 DB 저장 및 검색 테스트** (다음 단계)
3. ⏳ AI 서버 DB 연결 구현
4. ⏳ 추천 API 구현
5. ⏳ Spring 연동
