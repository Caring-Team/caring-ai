from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from models.institution import InstitutionRequest, InstitutionResponse
from models.user import Member, ElderlyProfile
from services.embedding_service import EmbeddingService
from services.database_service import DatabaseService
from utils.text_formatter import create_institution_text, create_user_profile_text

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 전역 서비스 인스턴스
embedding_service = None
db_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행"""
    global embedding_service, db_service
    
    logger.info("🚀 AI 서버 시작 중...")
    
    # 서비스 초기화
    embedding_service = EmbeddingService()
    db_service = DatabaseService()
    
    logger.info("✅ 모든 서비스 초기화 완료")
    
    yield
    
    # 종료 시 정리
    logger.info("🛑 AI 서버 종료 중...")
    if db_service:
        db_service.close()


# FastAPI 앱 생성
app = FastAPI(
    title="Caring AI Server",
    description="요양 기관 추천 AI 서버",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Caring AI Server is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "embedding_service": "loaded" if embedding_service else "not loaded",
        "database": "connected" if db_service else "not connected"
    }


@app.post("/api/v1/institutions/embeddings", response_model=InstitutionResponse)
async def create_institution_embedding(request: InstitutionRequest):
    """
    기능 1: 기관 정보를 받아서 임베딩 생성 및 저장
    
    Spring에서 기관이 등록될 때 호출됩니다.
    """
    try:
        logger.info(f"📥 기관 등록 요청 수신: ID={request.institution_id}, 이름={request.name}")
        
        # 1. 기관 정보 → 텍스트 변환
        institution_text = create_institution_text(
            name=request.name,
            institution_type=request.institution_type,
            address=request.address,
            specialized_diseases=request.specialized_diseases or [],
            service_types=request.service_types or [],
            operational_features=request.operational_features or [],
            facility_features=request.facility_features or [],
            opening_hours=request.opening_hours or "",
            description=request.description or ""
        )
        
        logger.info(f"📝 텍스트 변환 완료 (길이: {len(institution_text)}자)")
        logger.debug(f"변환된 텍스트:\n{institution_text}")
        
        # 2. 텍스트 → 임베딩 변환
        embedding = embedding_service.encode_text(institution_text)
        
        # 3. 메타데이터 준비
        metadata = {
            "name": request.name,
            "type": request.institution_type,
            "address": request.address,
            "specialized_diseases": request.specialized_diseases or [],
            "service_types": request.service_types or [],
            "operational_features": request.operational_features or [],
            "facility_features": request.facility_features or []
        }
        
        # 4. DB에 저장
        db_service.save_institution_embedding(
            institution_id=request.institution_id,
            embedding=embedding,
            original_text=institution_text,
            metadata=metadata
        )
        
        logger.info(f"✅ 기관 ID {request.institution_id} 처리 완료")
        
        return InstitutionResponse(
            success=True,
            institution_id=request.institution_id,
            message="기관 임베딩이 성공적으로 생성 및 저장되었습니다.",
            embedding_dimension=len(embedding)
        )
        
    except Exception as e:
        logger.error(f"❌ 기관 임베딩 생성 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"임베딩 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/api/v1/users/profile-text")
async def generate_user_profile_text(
    member: Member,
    elderly_profile: ElderlyProfile,
    additional_text: str = ""
):
    """
    기능 4: 사용자 데이터를 받아서 텍스트로 변환
    
    Spring에서 Member와 ElderlyProfile 정보를 보내면
    기관과 동일한 형식의 텍스트로 변환합니다.
    """
    try:
        logger.info(f"📥 사용자 프로필 텍스트 생성 요청: 회원={member.name}, 어르신={elderly_profile.name}")
        
        # 사용자 프로필 → 텍스트 변환
        user_text = create_user_profile_text(
            member_name=member.name,
            elderly_name=elderly_profile.name,
            age=elderly_profile.age,
            gender=elderly_profile.gender,
            activity_level=elderly_profile.activity_level.value,
            cognitive_level=elderly_profile.cognitive_level.value,
            care_grade=elderly_profile.care_grade or "",
            preferred_specialized_diseases=elderly_profile.preferred_specialized_diseases,
            preferred_service_types=elderly_profile.preferred_service_types,
            preferred_operational_features=elderly_profile.preferred_operational_features,
            preferred_facility_features=elderly_profile.preferred_facility_features,
            additional_text=additional_text
        )
        
        logger.info(f"✅ 사용자 프로필 텍스트 생성 완료 (길이: {len(user_text)}자)")
        
        return {
            "success": True,
            "member_id": member.member_id,
            "elderly_profile_id": elderly_profile.elderly_profile_id,
            "profile_text": user_text,
            "text_length": len(user_text)
        }
        
    except Exception as e:
        logger.error(f"❌ 사용자 프로필 텍스트 생성 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"텍스트 생성 중 오류가 발생했습니다: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
