from pydantic import BaseModel, Field
from typing import List, Optional


class InstitutionRequest(BaseModel):
    """Spring에서 받는 기관 등록 요청"""
    institution_id: int = Field(..., description="기관 고유 ID", alias="institutionId")
    name: str = Field(..., description="기관명", alias="name")
    institution_type: str = Field(..., description="기관 유형 (요양원, 주간보호센터 등)", alias="institutionType")
    address: str = Field(..., description="주소")
    
    # 태그 정보
    specialized_diseases: Optional[List[str]] = Field(default=[], description="전문 질환 (치매, 당뇨 등)", alias="specializedDiseases")
    service_types: Optional[List[str]] = Field(default=[], description="서비스 유형 (주간보호, 장기요양 등)", alias="serviceTypes")
    operational_features: Optional[List[str]] = Field(default=[], description="운영 특성 (치매 전담, 24시간 간호사 등)", alias="operationalFeatures")
    facility_features: Optional[List[str]] = Field(default=[], description="환경/시설 (정원, 예배실 등)", alias="facilityFeatures")
    
    # 추가 정보
    opening_hours: str = Field(default="", description="운영 시간", alias="openinggHours")
    description: str = Field(default="", description="기관 설명")
    
    class Config:
        json_schema_extra = {
            "example": {
                "institution_id": 1,
                "name": "사랑재 요양원",
                "institution_type": "요양원",
                "address": "서울시 송파구 올림픽로 123",
                "region": "서울시 송파구",
                "specialized_diseases": ["치매", "당뇨"],
                "service_types": ["주간보호", "장기요양"],
                "operational_features": ["치매 전담", "24시간 간호사"],
                "facility_features": ["정원", "예배실"],
                "operating_hours": "평일 08:00~20:00, 토요일 09:00~15:00",
                "description": "치매 교육을 받은 요양보호사가 다수 근무하며 친절을 강조하는 기관입니다."
            }
        }


class InstitutionResponse(BaseModel):
    """기관 등록 응답"""
    success: bool
    institution_id: int
    message: str
    embedding_dimension: int = 1024
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "institution_id": 1,
                "message": "기관 임베딩이 성공적으로 생성되었습니다.",
                "embedding_dimension": 1024
            }
        }
