-- pgvector extension 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 기관 임베딩 테이블 (벡터 저장)
CREATE TABLE IF NOT EXISTS institution_embeddings (
    id BIGSERIAL PRIMARY KEY,
    institution_id BIGINT NOT NULL UNIQUE,
    embedding vector(1024),  -- bge-m3 모델 (1024차원)
    original_text TEXT,  -- 임베딩 생성에 사용된 원본 텍스트 (디버깅/추적용)
    metadata JSONB,  -- 기관 메타데이터
    embedding_version INT DEFAULT 1,  -- 임베딩 버전 관리
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 벡터 유사도 검색용 인덱스 (IVFFlat)
CREATE INDEX IF NOT EXISTS idx_embedding_ivfflat 
ON institution_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- 일반 인덱스
CREATE INDEX IF NOT EXISTS idx_institution_id 
ON institution_embeddings(institution_id);

CREATE INDEX IF NOT EXISTS idx_metadata 
ON institution_embeddings USING GIN (metadata);

-- 업데이트 시간 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
DROP TRIGGER IF EXISTS update_institution_embeddings_updated_at ON institution_embeddings;
CREATE TRIGGER update_institution_embeddings_updated_at 
BEFORE UPDATE ON institution_embeddings 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- 샘플 쿼리 예시 (주석)
/*
-- Top 10 유사 기관 검색 예시
SELECT 
    institution_id,
    1 - (embedding <=> '[0.23, 0.45, ...]'::vector) AS similarity,
    metadata
FROM institution_embeddings
WHERE metadata->>'region' LIKE '서울%'
ORDER BY embedding <=> '[0.23, 0.45, ...]'::vector
LIMIT 10;

-- 특정 타입 필터링 검색
SELECT 
    institution_id,
    1 - (embedding <=> '[0.23, 0.45, ...]'::vector) AS similarity,
    metadata->>'name' as name,
    metadata->>'type' as type
FROM institution_embeddings
WHERE metadata->>'type' = '재활병원'
ORDER BY embedding <=> '[0.23, 0.45, ...]'::vector
LIMIT 10;
*/
