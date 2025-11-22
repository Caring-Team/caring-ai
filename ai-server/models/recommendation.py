from pydantic import BaseModel, Field
from typing import List, Optional


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


class RecommendationRequest(BaseModel):
    """추천 요청"""
    member: "Member" = Field(..., description="회원 정보")
    elderlyProfile: "ElderlyProfile" = Field(..., description="어르신 프로필")
    additionalText: Optional[str] = Field(default="", description="추가 요구사항")
    limit: int = Field(default=5, description="추천 기관 수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "member": {
                    "memberId": 1,
                    "name": "김보호자"
                },
                "elderlyProfile": {
                    "elderlyProfileId": 1,
                    "name": "김할머니",
                    "gender": "FEMALE",
                    "birthDate": "1942-03-15",
                    "activityLevel": "MEDIUM",
                    "cognitiveLevel": "MODERATE_DEMENTIA",
                    "longTermCareGrade": "GRADE_2"
                },
                "additionalText": "저희 어머니가 사람 많은 곳을 힘들어하세요",
                "limit": 5
            }
        }


class RecommendationResponse(BaseModel):
    """추천 응답"""
    success: bool = Field(..., description="성공 여부")
    memberId: int = Field(..., description="회원 ID")
    elderlyProfileId: int = Field(..., description="어르신 프로필 ID")
    totalResults: int = Field(..., description="총 결과 수")
    recommendations: List[RecommendationItem] = Field(..., description="추천 기관 리스트")
    responseTime: Optional[int] = Field(default=None, description="응답 시간 (ms)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "memberId": 1,
                "elderlyProfileId": 1,
                "totalResults": 5,
                "recommendations": [
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
                ],
                "responseTime": 850
            }
        }
