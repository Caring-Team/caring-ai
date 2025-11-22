from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import date


class Gender(str, Enum):
    """성별"""
    MALE = "MALE"
    FEMALE = "FEMALE"


class ActivityLevel(str, Enum):
    """활동 수준"""
    HIGH = "HIGH"  # 높음: 혼자 외출 가능하고 일상생활 대부분 스스로 가능
    MEDIUM = "MEDIUM"  # 보통: 실내 활동 위주, 짧은 거리 보행 가능
    LOW = "LOW"  # 낮음: 거동이 많이 불편하고 이동 시 도움 필요
    BEDRIDDEN = "BEDRIDDEN"  # 와상: 침대에서만 생활


class CognitiveLevel(str, Enum):
    """인지 수준"""
    NORMAL = "NORMAL"  # 정상: 인지 기능에 큰 문제 없음
    MILD_COGNITIVE_IMPAIRMENT = "MILD_COGNITIVE_IMPAIRMENT"  # 경도 인지 장애: 경미한 기억력 저하
    MILD_DEMENTIA = "MILD_DEMENTIA"  # 경증 치매: 일상생활에 약간의 지장
    MODERATE_DEMENTIA = "MODERATE_DEMENTIA"  # 중등도 치매: 치매 초기, 가끔 기억력 저하와 길 잃음
    SEVERE_DEMENTIA = "SEVERE_DEMENTIA"  # 중증 치매: 인지 저하가 심하고 지속적인 보호 필요


class LongTermCareGrade(str, Enum):
    """장기요양등급"""
    GRADE_1 = "GRADE_1"  # 1등급 (95점 이상)
    GRADE_2 = "GRADE_2"  # 2등급 (75~95점 미만)
    GRADE_3 = "GRADE_3"  # 3등급 (60~75점 미만)
    GRADE_4 = "GRADE_4"  # 4등급 (51~60점 미만)
    GRADE_5 = "GRADE_5"  # 5등급 (45~51점 미만)
    COGNITIVE = "COGNITIVE"  # 인지등급 (치매 어르신)
    NONE = "NONE"  # 등급 없음


class BloodType(str, Enum):
    """혈액형"""
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"
    UNKNOWN = "UNKNOWN"


class Member(BaseModel):
    """회원 정보"""
    memberId: int = Field(..., description="회원 ID", alias="memberId")
    name: str = Field(..., description="회원 이름")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "memberId": 1,
                "name": "김보호자"
            }
        }


class ElderlyProfile(BaseModel):
    """어르신 프로필 - Spring 엔티티와 완전히 동일한 구조"""
    
    # ID
    elderlyProfileId: int = Field(..., description="어르신 프로필 ID", alias="elderlyProfileId")
    
    # 기본 정보
    name: str = Field(..., description="어르신 성함")
    gender: Gender = Field(..., description="성별")
    birthDate: Optional[date] = Field(default=None, description="생년월일", alias="birthDate")
    bloodType: Optional[BloodType] = Field(default=None, description="혈액형", alias="bloodType")
    phoneNumber: Optional[str] = Field(default=None, description="연락처", alias="phoneNumber")
    
    # 건강 및 기능 상태
    activityLevel: Optional[ActivityLevel] = Field(default=None, description="활동 수준", alias="activityLevel")
    cognitiveLevel: Optional[CognitiveLevel] = Field(default=None, description="인지 수준", alias="cognitiveLevel")
    longTermCareGrade: Optional[LongTermCareGrade] = Field(default=None, description="장기 요양 등급", alias="longTermCareGrade")
    
    # 특이사항
    notes: Optional[str] = Field(default=None, description="특이사항 (최대 500자)")
    
    # 주소 (간단하게 문자열로 받기 - 필요시 Address 객체로 확장 가능)
    address: Optional[str] = Field(default=None, description="주소")
    
    # 위도/경도 (선택적)
    latitude: Optional[float] = Field(default=None, description="위도")
    longitude: Optional[float] = Field(default=None, description="경도")
    
    # 선호 태그 (AI 추천용 추가 필드)
    preferredSpecializedDiseases: List[str] = Field(
        default=[], 
        description="전문 질환 관련 선호",
        alias="preferredSpecializedDiseases"
    )
    preferredServiceTypes: List[str] = Field(
        default=[], 
        description="서비스 유형 선호",
        alias="preferredServiceTypes"
    )
    preferredOperationalFeatures: List[str] = Field(
        default=[], 
        description="운영 특성 선호",
        alias="preferredOperationalFeatures"
    )
    preferredFacilityFeatures: List[str] = Field(
        default=[], 
        description="환경/시설 선호",
        alias="preferredFacilityFeatures"
    )
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "elderlyProfileId": 1,
                "name": "김할머니",
                "gender": "FEMALE",
                "birthDate": "1942-03-15",
                "bloodType": "A",
                "phoneNumber": "010-1234-5678",
                "activityLevel": "MEDIUM",
                "cognitiveLevel": "MODERATE_DEMENTIA",
                "longTermCareGrade": "GRADE_2",
                "notes": "당뇨 약 복용 중, 매일 오후 2시에 복용",
                "address": "서울시 송파구 올림픽로 123",
                "latitude": 37.5145,
                "longitude": 127.1059,
                "preferredSpecializedDiseases": ["치매", "당뇨"],
                "preferredServiceTypes": ["주간보호", "장기요양"],
                "preferredOperationalFeatures": ["치매 전담", "24시간 간호사"],
                "preferredFacilityFeatures": ["정원", "예배실"]
            }
        }
