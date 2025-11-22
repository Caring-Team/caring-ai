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
