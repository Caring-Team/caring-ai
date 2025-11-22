from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """bge-m3 임베딩 생성 서비스"""
    
    def __init__(self):
        logger.info("🔄 bge-m3 모델 로드 시작...")
        self.model = SentenceTransformer('BAAI/bge-m3')
        logger.info("✅ bge-m3 모델 로드 완료 (1024차원)")
    
    def encode_text(self, text: str) -> np.ndarray:
        """텍스트를 임베딩 벡터로 변환"""
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            logger.info(f"✅ 임베딩 생성 완료 (차원: {len(embedding)})")
            return embedding
        except Exception as e:
            logger.error(f"❌ 임베딩 생성 실패: {str(e)}")
            raise
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """여러 텍스트를 배치로 변환"""
        try:
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            logger.info(f"✅ 배치 임베딩 생성 완료 ({len(texts)}개)")
            return embeddings
        except Exception as e:
            logger.error(f"❌ 배치 임베딩 생성 실패: {str(e)}")
            raise
