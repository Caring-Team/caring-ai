from pydantic import BaseModel, Field
from typing import List, Optional


class MemberInfo(BaseModel):
    """회원 정보"""
    memberId: int = Field(..., description="회원 ID")
    name: str = Field(..., description="회원 이름")
    preferredSpecializedDiseases: List[str] = Field(default=[], description="전문 질환 관련 선호 태그")
    preferredServiceTypes: List[str] = Field(default=[], description="서비스 유형 선호 태그")
    preferredOperationalFeatures: List[str] = Field(default=[], description="운영 특성 선호 태그")
    preferredFacilityFeatures: List[str] = Field(default=[], description="환경/시설 선호 태그")
    latitude: Optional[float] = Field(default=None, description="위치 정보 (위도)")
    longitude: Optional[float] = Field(default=None, description="위치 정보 (경도)")
    
    class Config:
        populate_by_name = True


class ElderlyInfo(BaseModel):
    """어르신 프로필 정보"""
    elderlyProfileId: int = Field(..., description="어르신 프로필 ID")
    name: str = Field(..., description="어르신 이름")
    gender: str = Field(..., description="성별")
    birthDate: Optional[str] = Field(default=None, description="생년월일")
    bloodType: Optional[str] = Field(default=None, description="혈액형")
    phoneNumber: Optional[str] = Field(default=None, description="연락처")
    longTermCareGrade: Optional[str] = Field(default=None, description="장기요양등급")
    activityLevel: Optional[str] = Field(default=None, description="활동 수준")
    cognitiveLevel: Optional[str] = Field(default=None, description="인지 수준")
    notes: Optional[str] = Field(default=None, description="특이사항")
    address: Optional[str] = Field(default=None, description="주소")
    latitude: Optional[float] = Field(default=None, description="위도")
    longitude: Optional[float] = Field(default=None, description="경도")
    
    class Config:
        populate_by_name = True


class RecommendationRequest(BaseModel):
    """추천 요청 (Spring에서 전달)"""
    member: MemberInfo = Field(..., description="회원 정보")
    elderly: ElderlyInfo = Field(..., description="어르신 프로필 정보")
    additionalText: Optional[str] = Field(default="", description="추가 요구사항")
    limit: int = Field(default=5, description="추천 기관 수")
    
    class Config:
        populate_by_name = True


class RecommendationItem(BaseModel):
    """추천 기관 항목"""
    institutionId: int = Field(..., description="기관 ID")
    similarity: float = Field(..., description="유사도 (0~1)")
    name: str = Field(..., description="기관 이름")
    type: str = Field(..., description="기관 유형")
    address: str = Field(..., description="주소")
    isAvailable: bool = Field(..., description="입소 가능 여부")
    tags: List[str] = Field(default=[], description="기관의 태그들")
    recommendationReason: str = Field(..., description="추천의 이유 설명 텍스트")
    
    class Config:
        json_schema_extra = {
            "example": {
                "institutionId": 1,
                "similarity": 0.92,
                "name": "사랑재 요양원",
                "type": "NURSING_HOME",
                "address": "서울시 송파구 올림픽로 123",
                "isAvailable": True,
                "tags": ["치매", "당뇨", "장기요양", "치매전담", "24시간간호사"],
                "recommendationReason": "치매 전문 케어와 24시간 간호사 상주로 어르신의 인지 상태에 맞는 전문적인 돌봄이 가능합니다."
            }
        }


class RecommendationResponse(BaseModel):
    """추천 응답"""
    success: bool = Field(..., description="성공 여부")
    institutions: List[RecommendationItem] = Field(..., description="추천 기관 리스트")
    totalCount: int = Field(..., description="총 결과 수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "totalCount": 5,
                "institutions": [
                    {
                        "institutionId": 1,
                        "similarity": 0.92,
                        "name": "사랑재 요양원",
                        "type": "NURSING_HOME",
                        "address": "서울시 송파구 올림픽로 123",
                        "isAvailable": True,
                        "tags": ["치매", "당뇨", "장기요양", "치매전담"],
                        "recommendationReason": "치매 전문 케어와 24시간 간호사 상주로 어르신의 인지 상태에 맞는 전문적인 돌봄이 가능합니다."
                    }
                ]
            }
        }
