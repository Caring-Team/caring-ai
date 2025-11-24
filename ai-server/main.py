from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
import time

from models.institution import InstitutionRequest, InstitutionResponse
from models.user import Member, ElderlyProfile
from models.recommendation import RecommendationResponse, RecommendationItem, RecommendationRequest
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
    elderlyProfile: ElderlyProfile,
    additionalText: str = ""
):
    """
    기능 4: 사용자 데이터를 받아서 텍스트로 변환
    
    Spring에서 Member와 ElderlyProfile 정보를 보내면
    기관과 동일한 형식의 텍스트로 변환합니다.
    """
    try:
        logger.info(f"📥 사용자 프로필 텍스트 생성 요청: 회원={member.name}, 어르신={elderlyProfile.name}")
        
        # 사용자 프로필 → 텍스트 변환
        user_text = create_user_profile_text(
            member_name=member.name,
            elderly_name=elderlyProfile.name,
            gender=elderlyProfile.gender.value,
            birth_date=str(elderlyProfile.birthDate) if elderlyProfile.birthDate else "",
            activity_level=elderlyProfile.activityLevel.value if elderlyProfile.activityLevel else "",
            cognitive_level=elderlyProfile.cognitiveLevel.value if elderlyProfile.cognitiveLevel else "",
            long_term_care_grade=elderlyProfile.longTermCareGrade.value if elderlyProfile.longTermCareGrade else "",
            notes=elderlyProfile.notes or "",
            address=elderlyProfile.address or "",
            preferred_specialized_diseases=elderlyProfile.preferredSpecializedDiseases,
            preferred_service_types=elderlyProfile.preferredServiceTypes,
            preferred_operational_features=elderlyProfile.preferredOperationalFeatures,
            preferred_facility_features=elderlyProfile.preferredFacilityFeatures,
            additional_text=additionalText
        )
        
        logger.info(f"✅ 사용자 프로필 텍스트 생성 완료 (길이: {len(user_text)}자)")
        
        return {
            "success": True,
            "memberId": member.memberId,
            "elderlyProfileId": elderlyProfile.elderlyProfileId,
            "profileText": user_text,
            "textLength": len(user_text)
        }
        
    except Exception as e:
        logger.error(f"❌ 사용자 프로필 텍스트 생성 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"텍스트 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/api/v1/users/profile-embedding")
async def generate_user_profile_embedding(
    member: Member,
    elderlyProfile: ElderlyProfile,
    additionalText: str = ""
):
    """
    기능 5: 사용자 데이터를 받아서 임베딩으로 변환
    
    Spring에서 Member와 ElderlyProfile 정보를 보내면
    1. 텍스트로 변환
    2. 임베딩으로 변환
    3. 임베딩 벡터 반환
    """
    try:
        logger.info(f"📥 사용자 프로필 임베딩 생성 요청: 회원={member.name}, 어르신={elderlyProfile.name}")
        
        # 1. 사용자 프로필 → 텍스트 변환
        user_text = create_user_profile_text(
            member_name=member.name,
            elderly_name=elderlyProfile.name,
            gender=elderlyProfile.gender.value,
            birth_date=str(elderlyProfile.birthDate) if elderlyProfile.birthDate else "",
            activity_level=elderlyProfile.activityLevel.value if elderlyProfile.activityLevel else "",
            cognitive_level=elderlyProfile.cognitiveLevel.value if elderlyProfile.cognitiveLevel else "",
            long_term_care_grade=elderlyProfile.longTermCareGrade.value if elderlyProfile.longTermCareGrade else "",
            notes=elderlyProfile.notes or "",
            address=elderlyProfile.address or "",
            preferred_specialized_diseases=elderlyProfile.preferredSpecializedDiseases,
            preferred_service_types=elderlyProfile.preferredServiceTypes,
            preferred_operational_features=elderlyProfile.preferredOperationalFeatures,
            preferred_facility_features=elderlyProfile.preferredFacilityFeatures,
            additional_text=additionalText
        )
        
        logger.info(f"📝 텍스트 변환 완료 (길이: {len(user_text)}자)")
        
        # 2. 텍스트 → 임베딩 변환
        embedding = embedding_service.encode_text(user_text)
        
        logger.info(f"✅ 사용자 프로필 임베딩 생성 완료 (차원: {len(embedding)})")
        
        return {
            "success": True,
            "memberId": member.memberId,
            "elderlyProfileId": elderlyProfile.elderlyProfileId,
            "profileText": user_text,
            "embedding": embedding.tolist(),  # numpy array를 list로 변환
            "embeddingDimension": len(embedding)
        }
        
    except Exception as e:
        logger.error(f"❌ 사용자 프로필 임베딩 생성 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"임베딩 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/api/v1/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    기능 3: 사용자 프로필 기반 기관 추천
    
    Spring의 RecommendationRequest 형식으로 요청을 받아
    사용자 정보를 임베딩으로 변환한 후 pgvector로 유사한 기관을 검색하고
    RecommendationItem 형식으로 반환합니다.
    """
    try:
        start_time = time.time()
        
        member = request.member
        elderly = request.elderly
        
        logger.info(f"📥 기관 추천 요청: 회원={member.name}, 어르신={elderly.name}, limit={request.limit}")
        
        # 1. 사용자 프로필 → 텍스트 변환
        user_text = create_user_profile_text(
            member_name=member.name,
            elderly_name=elderly.name,
            gender=elderly.gender,
            birth_date=elderly.birthDate or "",
            activity_level=elderly.activityLevel or "",
            cognitive_level=elderly.cognitiveLevel or "",
            long_term_care_grade=elderly.longTermCareGrade or "",
            notes=elderly.notes or "",
            address=elderly.address or "",
            preferred_specialized_diseases=member.preferredSpecializedDiseases,
            preferred_service_types=member.preferredServiceTypes,
            preferred_operational_features=member.preferredOperationalFeatures,
            preferred_facility_features=member.preferredFacilityFeatures,
            additional_text=request.additionalText or ""
        )
        
        # 2. 텍스트 → 임베딩 변환
        user_embedding = embedding_service.encode_text(user_text)
        
        # 3. 유사 기관 검색 (limit보다 많이 가져와서 필터링 여유 확보)
        similar_institutions = db_service.search_similar_institutions(
            user_embedding=user_embedding,
            limit=request.limit * 2,  # 필터링을 위해 2배로 조회
            min_similarity=0.0
        )
        
        # 4. RecommendationItem 형식으로 변환
        recommendations = []
        for inst in similar_institutions[:request.limit]:  # limit만큼만 반환
            metadata = inst.get("metadata", {})
            
            # 태그 리스트 생성 (전문질환, 서비스, 운영특성, 시설 모두 합침)
            tags = []
            tags.extend(metadata.get("specialized_diseases", []))
            tags.extend(metadata.get("service_types", []))
            tags.extend(metadata.get("operational_features", []))
            tags.extend(metadata.get("facility_features", []))
            
            # TODO: 추천 이유는 나중에 LLM으로 생성 (기능 9)
            # 지금은 임시로 간단한 텍스트 생성
            recommendation_reason = f"유사도 {inst['similarity']:.2%}로 매칭되었습니다."
            
            recommendation_item = RecommendationItem(
                institutionId=inst["institutionId"],
                similarity=inst["similarity"],
                name=metadata.get("name", ""),
                type=metadata.get("type", ""),
                address=metadata.get("address", ""),
                isAvailable=True,  # TODO: Spring에서 입소 가능 여부 정보 필요
                tags=tags,
                recommendationReason=recommendation_reason
            )
            
            recommendations.append(recommendation_item)
        
        # 5. 응답 시간 계산
        response_time = int((time.time() - start_time) * 1000)  # ms 단위
        
        logger.info(f"✅ 기관 추천 완료: {len(recommendations)}개 반환 (응답시간: {response_time}ms)")
        
        return RecommendationResponse(
            success=True,
            institutions=recommendations,
            totalCount=len(recommendations)
        )
        
    except Exception as e:
        logger.error(f"❌ 기관 추천 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"기관 추천 중 오류가 발생했습니다: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)