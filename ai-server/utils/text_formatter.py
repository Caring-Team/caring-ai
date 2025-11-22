from typing import List


def create_institution_text(
    name: str,
    institution_type: str,
    address: str,
    specialized_diseases: List[str],
    service_types: List[str],
    operational_features: List[str],
    facility_features: List[str],
    opening_hours: str,
    description: str
) -> str:
    """
    기관 정보를 구조화된 텍스트로 변환
    어르신 프로필과 동일한 관점(건강, 서비스, 환경)으로 작성
    """
    
    text_parts = []
    
    # 기본 정보
    text_parts.append(f"[기관 정보]")
    text_parts.append(f"- 기본 정보:")
    text_parts.append(f"  - 기관명: {name}")
    text_parts.append(f"  - 기관 유형: {institution_type}")
    
    # 운영 정보
    if opening_hours:
        text_parts.append(f"- 운영 정보:")
        text_parts.append(f"  - 운영 시간: {opening_hours}")
    
    # 기관 태그
    text_parts.append(f"- 기관 태그:")
    if specialized_diseases:
        text_parts.append(f"  - 전문 질환: {', '.join(specialized_diseases)}")
    if service_types:
        text_parts.append(f"  - 서비스 유형: {', '.join(service_types)}")
    if operational_features:
        text_parts.append(f"  - 운영 특성: {', '.join(operational_features)}")
    if facility_features:
        text_parts.append(f"  - 환경/시설: {', '.join(facility_features)}")
    
    # 기관 설명
    if description:
        text_parts.append(f"- 기관 설명: {description}")
    
    return "\n".join(text_parts)


def create_user_profile_text(
    member_name: str,
    elderly_name: str,
    gender: str,
    birth_date: str,
    activity_level: str,
    cognitive_level: str,
    long_term_care_grade: str,
    notes: str,
    address: str,
    preferred_specialized_diseases: List[str],
    preferred_service_types: List[str],
    preferred_operational_features: List[str],
    preferred_facility_features: List[str],
    additional_text: str = ""
) -> str:
    """
    사용자(어르신) 프로필을 구조화된 텍스트로 변환
    기관 정보와 동일한 관점으로 작성하여 임베딩 공간에서 유사도 계산이 잘 되도록 함
    """
    
    # 활동 수준 설명
    activity_descriptions = {
        "HIGH": "높음 - 혼자 외출 가능하고 일상생활 대부분 스스로 가능",
        "MEDIUM": "보통 - 실내 활동 위주, 짧은 거리 보행 가능",
        "LOW": "낮음 - 거동이 많이 불편하고 이동 시 도움 필요",
        "BEDRIDDEN": "와상 - 침대에서만 생활"
    }
    
    # 인지 수준 설명
    cognitive_descriptions = {
        "NORMAL": "정상 - 인지 기능에 큰 문제 없음",
        "MILD_COGNITIVE_IMPAIRMENT": "경도 인지 장애 - 경미한 기억력 저하가 있습니다",
        "MILD_DEMENTIA": "경증 치매 - 일상생활에 약간의 지장이 가는 수준입니다",
        "MODERATE_DEMENTIA": "중등도 치매 - 치매 초기로 가끔 기억력 저하와 길 잃음이 있습니다",
        "SEVERE_DEMENTIA": "중증 치매 - 인지 저하가 심하고 지속적인 보호가 필요합니다"
    }
    
    # 장기요양등급 설명
    care_grade_descriptions = {
        "GRADE_1": "1등급 (95점 이상)",
        "GRADE_2": "2등급 (75~95점 미만)",
        "GRADE_3": "3등급 (60~75점 미만)",
        "GRADE_4": "4등급 (51~60점 미만)",
        "GRADE_5": "5등급 (45~51점 미만)",
        "COGNITIVE": "인지등급 (치매 어르신)",
        "NONE": "등급 없음"
    }
    
    # 나이 계산 (birth_date가 있는 경우)
    age_text = ""
    if birth_date:
        from datetime import datetime
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            age = datetime.now().year - birth.year
            age_text = f"만 {age}세"
        except:
            age_text = ""
    
    text_parts = []
    
    # 기본 정보
    text_parts.append(f"[어르신 프로필]")
    text_parts.append(f"- 기본 정보:")
    text_parts.append(f"  - 이름: {elderly_name}")
    if age_text:
        text_parts.append(f"  - 연령: {age_text}")
    text_parts.append(f"  - 성별: {gender}")
    
    # 건강 및 기능 상태
    text_parts.append(f"- 건강 및 기능 상태:")
    if activity_level:
        text_parts.append(f"  - 활동 수준: {activity_descriptions.get(activity_level, activity_level)}")
    if cognitive_level:
        text_parts.append(f"  - 인지 수준: {cognitive_descriptions.get(cognitive_level, cognitive_level)}")
    if long_term_care_grade:
        text_parts.append(f"  - 장기 요양 등급: {care_grade_descriptions.get(long_term_care_grade, long_term_care_grade)}")
    
    # 특이사항
    if notes:
        text_parts.append(f"- 특이사항: {notes}")
    
    # 주소
    if address:
        text_parts.append(f"- 주소: {address}")
    
    # 선호 태그
    text_parts.append(f"- 선호 태그:")
    if preferred_specialized_diseases:
        text_parts.append(f"  - 전문 질환: {', '.join(preferred_specialized_diseases)}")
    if preferred_service_types:
        text_parts.append(f"  - 서비스 유형: {', '.join(preferred_service_types)}")
    if preferred_operational_features:
        text_parts.append(f"  - 운영 특성: {', '.join(preferred_operational_features)}")
    if preferred_facility_features:
        text_parts.append(f"  - 환경/시설: {', '.join(preferred_facility_features)}")
    
    # 추가 요구사항
    if additional_text:
        text_parts.append(f"- 추가 요구사항: {additional_text}")
    
    return "\n".join(text_parts)
