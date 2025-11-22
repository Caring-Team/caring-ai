import psycopg2
from psycopg2.extras import Json
import numpy as np
import logging
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class DatabaseService:
    """PostgreSQL + pgvector 연결 및 저장 서비스"""
    
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """DB 연결"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "caring"),
                user=os.getenv("DB_USER", "mychan"),
                password=os.getenv("DB_PASSWORD", "na58745874@")
            )
            logger.info("✅ PostgreSQL 연결 성공")
        except Exception as e:
            logger.error(f"❌ DB 연결 실패: {str(e)}")
            raise
    
    def save_institution_embedding(
        self,
        institution_id: int,
        embedding: np.ndarray,
        original_text: str,
        metadata: dict
    ) -> bool:
        """기관 임베딩 저장"""
        try:
            cursor = self.conn.cursor()
            
            # numpy array를 list로 변환
            embedding_list = embedding.tolist()
            
            # UPSERT 쿼리 (institution_id가 있으면 UPDATE, 없으면 INSERT)
            query = """
            INSERT INTO institution_embeddings 
                (institution_id, embedding, original_text, metadata, embedding_version)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (institution_id) 
            DO UPDATE SET
                embedding = EXCLUDED.embedding,
                original_text = EXCLUDED.original_text,
                metadata = EXCLUDED.metadata,
                embedding_version = EXCLUDED.embedding_version,
                updated_at = NOW()
            """
            
            cursor.execute(query, (
                institution_id,
                embedding_list,
                original_text,
                Json(metadata),
                1  # embedding_version
            ))
            
            self.conn.commit()
            cursor.close()
            
            logger.info(f"✅ 기관 ID {institution_id} 임베딩 저장 완료")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ 임베딩 저장 실패: {str(e)}")
            raise
    
    def search_similar_institutions(
        self,
        user_embedding: np.ndarray,
        limit: int = 10,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        기능 7: 사용자 임베딩과 유사한 기관 검색
        
        pgvector의 코사인 유사도를 사용하여 검색합니다.
        <=> 연산자는 코사인 거리를 계산하며, IVFFlat 인덱스로 최적화됩니다.
        
        Args:
            user_embedding: 사용자 프로필 임베딩 벡터 (1024차원)
            limit: 반환할 최대 기관 수 (기본 10개)
            min_similarity: 최소 유사도 threshold (0~1, 기본 0.0)
        
        Returns:
            유사 기관 리스트 [
                {
                    "institutionId": int,
                    "similarity": float,
                    "metadata": dict,
                    "originalText": str
                },
                ...
            ]
        """
        try:
            cursor = self.conn.cursor()
            
            # numpy array를 list로 변환
            embedding_list = user_embedding.tolist()
            
            # pgvector 코사인 유사도 검색 쿼리
            # <=> 연산자: 코사인 거리 (0에 가까울수록 유사)
            # 1 - 코사인 거리 = 코사인 유사도 (1에 가까울수록 유사, 0~1 범위)
            query = """
            SELECT 
                institution_id,
                1 - (embedding <=> %s::vector) AS similarity,
                metadata,
                original_text
            FROM institution_embeddings
            WHERE 1 - (embedding <=> %s::vector) >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """
            
            cursor.execute(query, (
                embedding_list,
                embedding_list,
                min_similarity,
                embedding_list,
                limit
            ))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "institutionId": row[0],
                    "similarity": float(row[1]),
                    "metadata": row[2],
                    "originalText": row[3]
                })
            
            cursor.close()
            
            top_similarity = results[0]['similarity'] if results else 0
            logger.info(f"✅ 유사 기관 검색 완료: {len(results)}개 발견 (상위 유사도: {top_similarity:.4f})")
            return results
            
        except Exception as e:
            logger.error(f"❌ 유사도 검색 실패: {str(e)}")
            raise
    
    def close(self):
        """DB 연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("DB 연결 종료")
