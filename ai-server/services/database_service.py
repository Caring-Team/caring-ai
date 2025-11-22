import psycopg2
from psycopg2.extras import Json
import numpy as np
import logging
from typing import Optional
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
    
    def close(self):
        """DB 연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("DB 연결 종료")
