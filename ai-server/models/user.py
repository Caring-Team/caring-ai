from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ActivityLevel(str, Enum):
    """활동 수준"""
    HIGH = "HIGH"  # 혼자 외출 가능하고 일상생활 대부분 스스로 가능
    MID = "MID"  # 실내 활동 위주, 짧은 거리 보행 가능
    LOW = "LOW"  # 거동이 많이 불편하고 이동 시 도움 필요
    BEDRIDDEN = "BEDRIDDEN"  # 침대에서만 생활


class CognitiveLevel(str, Enum):
    """인지 수준"""
    NORMAL = "NORMAL"  # 인지 기능에 큰 문제 없음
    MILD_COGNITIVE_IMPAIRMENT = "MILD_COGNITIVE_IMPAIRMENT"  # 경미한 기억력 저하
    MILD_DEMENTIA = "MILD_DEMENTIA"  # 일상생활에 약간의 지장
    MODERATE_DEMENTIA = "MODERATE_DEMENTIA"  # 치매 초기, 가끔 기억력 저하와 길 잃음
    SEVERE_DEMENTIA = "SEVERE_DEMENTIA"  # 인지 저하가 심하고 지속적인 보호 필요


class Member(BaseModel):
    """회원 정보"""
    member_id: int = Field(..., description="회원 ID")
    name: str = Field(..., description="회원 이름")
    
    class Config:
        json_schema_extra = {
            "example": {
                "member_id": 1,
                "name": "김보호자"
            }
        }


class ElderlyProfile(BaseModel):
    """어르신 프로필"""
    elderly_profile_id: int = Field(..., description="어르신 프로필 ID")
    name: str = Field(..., description="어르신 성함")
    age: int = Field(..., description="만 나이")
    gender: str = Field(..., description="성별 (남성/여성)")
    
    # 건강 및 기능 상태
    activity_level: ActivityLevel = Field(..., description="활동 수준")
    cognitive_level: CognitiveLevel = Field(..., description="인지 수준")
    care_grade: Optional[str] = Field(default=None, description="장기 요양 등급 (1~5등급)")
    
    # 선호 태그
    preferred_specialized_diseases: List[str] = Field(default=[], description="전문 질환 관련 선호")
    preferred_service_types: List[str] = Field(default=[], description="서비스 유형 선호")
    preferred_operational_features: List[str] = Field(default=[], description="운영 특성 선호")
    preferred_facility_features: List[str] = Field(default=[], description="환경/시설 선호")
    
    class Config:
        json_schema_extra = {
            "example": {
                "elderly_profile_id": 1,
                "name": "김할머니",
                "age": 82,
                "gender": "여성",
                "activity_level": "MID",
                "cognitive_level": "MODERATE_DEMENTIA",
                "care_grade": "2등급",
                "preferred_specialized_diseases": ["치매", "당뇨"],
                "preferred_service_types": ["주간보호", "장기요양"],
                "preferred_operational_features": ["치매 전담", "24시간 간호사"],
                "preferred_facility_features": ["정원", "예배실"]
            }
        }
