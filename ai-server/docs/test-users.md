# 테스트용 사용자 및 어르신 프로필 데이터

Swagger에서 `POST /api/v1/recommendations`에 사용할 테스트 데이터입니다.

---

## 테스트 사용자 1: 치매 초기 + 당뇨 환자

이 사용자 프로필은 등록된 10개 기관 중 여러 기관과 매칭될 수 있도록 설계되었습니다.

### 예상 매칭 기관:
- **사랑재 요양원** (치매 + 당뇨 전문)
- **햇살 주간보호센터** (치매 초기 전문)
- **행복한집 주간보호센터** (당뇨 관리)
- **평화의집 요양원** (치매 + 당뇨)
- **참사랑 요양원** (고급 치매 케어)

```json
{
  "member": {
    "memberId": 1,
    "name": "김보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 1,
    "name": "김영희",
    "gender": "FEMALE",
    "birthDate": "1942-05-20",
    "bloodType": "A",
    "phoneNumber": "010-1234-5678",
    "activityLevel": "MEDIUM",
    "cognitiveLevel": "MODERATE_DEMENTIA",
    "longTermCareGrade": "GRADE_2",
    "notes": "당뇨 약 복용 중, 매일 오후 2시 복용. 가끔 길을 잃어버리는 증상이 있습니다.",
    "address": "서울시 송파구 올림픽로 300",
    "latitude": 37.5145,
    "longitude": 127.1059,
    "preferredSpecializedDiseases": ["치매", "당뇨"],
    "preferredServiceTypes": ["주간보호", "장기요양"],
    "preferredOperationalFeatures": ["치매전담", "24시간간호사", "영양사배치"],
    "preferredFacilityFeatures": ["정원", "야외공간", "편안한분위기"]
  },
  "additionalText": "저희 어머니께서 사람이 너무 많은 곳은 힘들어하세요. 소규모로 운영되는 곳이면 좋겠고, 정원이나 산책할 수 있는 공간이 있으면 더욱 좋겠습니다. 치매 초기라 인지 활동 프로그램도 필요합니다.",
  "limit": 5
}
```

---

## 테스트 사용자 2: 뇌졸중 재활 환자

재활 전문 기관과 매칭하기 위한 프로필입니다.

### 예상 매칭 기관:
- **푸른솔 요양원** (뇌졸중 재활)
- **새봄 주간보호센터** (중증 환자 재활)

```json
{
  "member": {
    "memberId": 2,
    "name": "이보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 2,
    "name": "박철수",
    "gender": "MALE",
    "birthDate": "1945-08-15",
    "bloodType": "B",
    "phoneNumber": "010-2345-6789",
    "activityLevel": "LOW",
    "cognitiveLevel": "NORMAL",
    "longTermCareGrade": "GRADE_3",
    "notes": "6개월 전 뇌졸중으로 쓰러진 후 오른쪽 팔다리가 불편합니다. 적극적인 재활 치료가 필요합니다.",
    "address": "경기도 성남시 분당구 판교역로 500",
    "latitude": 37.3952,
    "longitude": 127.1113,
    "preferredSpecializedDiseases": ["뇌졸중", "재활"],
    "preferredServiceTypes": ["재활서비스", "물리치료"],
    "preferredOperationalFeatures": ["물리치료사", "재활 전문의"],
    "preferredFacilityFeatures": ["재활치료실", "운동실", "엘리베이터"]
  },
  "additionalText": "아버지께서 뇌졸중 후유증으로 재활 치료가 절실합니다. 물리치료사가 상주하고 최신 재활 장비가 있는 곳을 찾고 있습니다.",
  "limit": 5
}
```

---

## 테스트 사용자 3: 재가 돌봄 서비스 희망

집에서 돌봄을 받고 싶어하는 프로필입니다.

### 예상 매칭 기관:
- **소망 재가돌봄 서비스**
- **은빛 재가돌봄 서비스**

```json
{
  "member": {
    "memberId": 3,
    "name": "최보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 3,
    "name": "최순자",
    "gender": "FEMALE",
    "birthDate": "1948-12-03",
    "bloodType": "O",
    "phoneNumber": "010-3456-7890",
    "activityLevel": "MEDIUM",
    "cognitiveLevel": "MILD_COGNITIVE_IMPAIRMENT",
    "longTermCareGrade": "GRADE_4",
    "notes": "집에서 생활하길 원하시고, 정기적인 방문 간호와 목욕 서비스가 필요합니다.",
    "address": "서울시 서초구 반포대로 100",
    "latitude": 37.5012,
    "longitude": 127.0054,
    "preferredSpecializedDiseases": [],
    "preferredServiceTypes": ["방문요양", "방문간호", "방문목욕", "재가돌봄"],
    "preferredOperationalFeatures": ["자격증보유직원"],
    "preferredFacilityFeatures": []
  },
  "additionalText": "어머니께서 익숙한 집에서 생활하기를 원하십니다. 일주일에 3회 정도 방문 요양 서비스와 주 1회 방문 목욕 서비스가 필요합니다.",
  "limit": 5
}
```

---

## 테스트 사용자 4: 가톨릭 신자 (종교 시설 선호)

종교 시설이 있는 기관을 선호하는 프로필입니다.

### 예상 매칭 기관:
- **평화의집 요양원** (가톨릭)

```json
{
  "member": {
    "memberId": 4,
    "name": "정보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 4,
    "name": "정마리아",
    "gender": "FEMALE",
    "birthDate": "1940-03-25",
    "bloodType": "AB",
    "phoneNumber": "010-4567-8901",
    "activityLevel": "MEDIUM",
    "cognitiveLevel": "MILD_DEMENTIA",
    "longTermCareGrade": "GRADE_2",
    "notes": "평생 가톨릭 신자로 매일 미사 참례를 원하십니다. 고혈압 약 복용 중입니다.",
    "address": "경기도 고양시 일산동구 중앙로 500",
    "latitude": 37.6584,
    "longitude": 126.7729,
    "preferredSpecializedDiseases": ["치매", "고혈압"],
    "preferredServiceTypes": ["장기요양"],
    "preferredOperationalFeatures": ["24시간간호사"],
    "preferredFacilityFeatures": ["예배실", "정원", "산책로"]
  },
  "additionalText": "어머니께서 가톨릭 신앙이 깊으셔서 매일 미사와 기도 시간이 있는 요양원을 찾고 있습니다. 가톨릭 정신을 바탕으로 운영되는 곳이면 더욱 좋겠습니다.",
  "limit": 5
}
```

---

## 테스트 사용자 5: 고급 케어 희망 (프리미엄)

프리미엄 케어를 원하는 프로필입니다.

### 예상 매칭 기관:
- **참사랑 요양원** (고급 치매 케어)
- **은빛마을 실버타운** (해당 기관이 없지만 유사 타입)

```json
{
  "member": {
    "memberId": 5,
    "name": "한보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 5,
    "name": "한영숙",
    "gender": "FEMALE",
    "birthDate": "1943-07-10",
    "bloodType": "A",
    "phoneNumber": "010-5678-9012",
    "activityLevel": "LOW",
    "cognitiveLevel": "SEVERE_DEMENTIA",
    "longTermCareGrade": "GRADE_1",
    "notes": "중증 치매로 24시간 집중 케어가 필요합니다. 배회 증상이 있어 안전 시설이 필수입니다.",
    "address": "서울시 강남구 도곡로 400",
    "latitude": 37.4923,
    "longitude": 127.0538,
    "preferredSpecializedDiseases": ["치매"],
    "preferredServiceTypes": ["장기요양"],
    "preferredOperationalFeatures": ["치매전담", "24시간간호사", "의사상주"],
    "preferredFacilityFeatures": ["개인실", "의료실", "응급시스템", "CCTV"]
  },
  "additionalText": "어머니께서 중증 치매로 1:3 집중 케어가 필요합니다. 배회 감지 시스템과 안전 시설이 완비된 곳을 찾고 있으며, 가족 상담 프로그램도 있으면 좋겠습니다. 비용보다는 케어의 질이 우선입니다.",
  "limit": 5
}
```

---

# 테스트용 사용자 및 어르신 프로필 데이터 (태그 ID 버전)

Swagger에서 `POST /api/v1/recommendations`에 사용할 테스트 데이터입니다.

**Spring에서 태그 ID로 전달하는 경우를 위한 버전입니다.**

---

## 테스트 사용자 1: 치매 초기 + 당뇨 환자

이 사용자 프로필은 등록된 10개 기관 중 여러 기관과 매칭될 수 있도록 설계되었습니다.

### 예상 매칭 기관:
- **사랑재 요양원** (치매 + 당뇨 전문)
- **햇살 주간보호센터** (치매 초기 전문)
- **행복한집 주간보호센터** (당뇨 관리)
- **평화의집 요양원** (치매 + 당뇨)
- **참사랑 요양원** (고급 치매 케어)

### 태그 ID 버전:
```json
{
  "member": {
    "memberId": 1,
    "name": "김보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 1,
    "name": "김영희",
    "gender": "FEMALE",
    "birthDate": "1942-05-20",
    "bloodType": "A",
    "phoneNumber": "010-1234-5678",
    "activityLevel": "MEDIUM",
    "cognitiveLevel": "MODERATE_DEMENTIA",
    "longTermCareGrade": "GRADE_2",
    "notes": "당뇨 약 복용 중, 매일 오후 2시 복용. 가끔 길을 잃어버리는 증상이 있습니다.",
    "address": "서울시 송파구 올림픽로 300",
    "latitude": 37.5145,
    "longitude": 127.1059,
    "preferredTagIds": [1, 4, 16, 18, 31, 33, 35, 41, 47, 48, 70]
  },
  "additionalText": "저희 어머니께서 사람이 너무 많은 곳은 힘들어하세요. 소규모로 운영되는 곳이면 좋겠고, 정원이나 산책할 수 있는 공간이 있으면 더욱 좋겠습니다. 치매 초기라 인지 활동 프로그램도 필요합니다.",
  "limit": 5
}
```
**태그 설명:**
- 1: 치매 (SPECIALIZATION)
- 4: 당뇨 (SPECIALIZATION)
- 16: 주간보호 (SERVICE)
- 18: 장기요양 (SERVICE)
- 31: 치매전담 (OPERATION)
- 33: 24시간간호사 (OPERATION)
- 35: 영양사배치 (OPERATION)
- 41: 소규모 (OPERATION)
- 47: 정원 (ENVIRONMENT)
- 48: 야외공간 (ENVIRONMENT)
- 70: 편안한분위기 (REVIEW)

---

## 테스트 사용자 2: 뇌졸중 재활 환자

재활 전문 기관과 매칭하기 위한 프로필입니다.

### 예상 매칭 기관:
- **푸른솔 요양원** (뇌졸중 재활)
- **새봄 주간보호센터** (중증 환자 재활)

### 태그 ID 버전:
```json
{
  "member": {
    "memberId": 2,
    "name": "이보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 2,
    "name": "박철수",
    "gender": "MALE",
    "birthDate": "1945-08-15",
    "bloodType": "B",
    "phoneNumber": "010-2345-6789",
    "activityLevel": "LOW",
    "cognitiveLevel": "NORMAL",
    "longTermCareGrade": "GRADE_3",
    "notes": "6개월 전 뇌졸중으로 쓰러진 후 오른쪽 팔다리가 불편합니다. 적극적인 재활 치료가 필요합니다.",
    "address": "경기도 성남시 분당구 판교역로 500",
    "latitude": 37.3952,
    "longitude": 127.1113,
    "preferredTagIds": [2, 11, 18, 24, 36, 43, 49, 50, 64]
  },
  "additionalText": "아버지께서 뇌졸중 후유증으로 재활 치료가 절실합니다. 물리치료사가 상주하고 최신 재활 장비가 있는 곳을 찾고 있습니다.",
  "limit": 5
}
```
**태그 설명:**
- 2: 뇌졸중 (SPECIALIZATION)
- 11: 재활 (SPECIALIZATION)
- 18: 장기요양 (SERVICE)
- 24: 재활서비스 (SERVICE)
- 36: 물리치료사 (OPERATION)
- 43: 엘리베이터 (ENVIRONMENT)
- 49: 운동실 (ENVIRONMENT)
- 50: 재활치료실 (ENVIRONMENT)
- 64: 전문적인케어 (REVIEW)

---

## 테스트 사용자 3: 재가 돌봄 서비스 희망

집에서 돌봄을 받고 싶어하는 프로필입니다.

### 예상 매칭 기관:
- **소망 재가돌봄 서비스**
- **은빛 재가돌봄 서비스**

### 태그 ID 버전:
```json
{
  "member": {
    "memberId": 3,
    "name": "최보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 3,
    "name": "최순자",
    "gender": "FEMALE",
    "birthDate": "1948-12-03",
    "bloodType": "O",
    "phoneNumber": "010-3456-7890",
    "activityLevel": "MEDIUM",
    "cognitiveLevel": "MILD_COGNITIVE_IMPAIRMENT",
    "longTermCareGrade": "GRADE_4",
    "notes": "집에서 생활하길 원하시고, 정기적인 방문 간호와 목욕 서비스가 필요합니다.",
    "address": "서울시 서초구 반포대로 100",
    "latitude": 37.5012,
    "longitude": 127.0054,
    "preferredTagIds": [19, 20, 21, 22, 23, 32, 68, 73, 78]
  },
  "additionalText": "어머니께서 익숙한 집에서 생활하기를 원하십니다. 일주일에 3회 정도 방문 요양 서비스와 주 1회 방문 목욕 서비스가 필요합니다.",
  "limit": 5
}
```
**태그 설명:**
- 19: 방문요양 (SERVICE)
- 20: 방문간호 (SERVICE)
- 21: 방문목욕 (SERVICE)
- 22: 재가돌봄 (SERVICE)
- 23: 식사배달 (SERVICE)
- 32: 자격증보유직원 (OPERATION)
- 68: 소통잘됨 (REVIEW)
- 73: 합리적인가격 (REVIEW)
- 78: 투명한운영 (REVIEW)

---

## 테스트 사용자 4: 가톨릭 신자 (종교 시설 선호)

종교 시설이 있는 기관을 선호하는 프로필입니다.

### 예상 매칭 기관:
- **평화의집 요양원** (가톨릭)

### 태그 ID 버전:
```json
{
  "member": {
    "memberId": 4,
    "name": "정보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 4,
    "name": "정마리아",
    "gender": "FEMALE",
    "birthDate": "1940-03-25",
    "bloodType": "AB",
    "phoneNumber": "010-4567-8901",
    "activityLevel": "MEDIUM",
    "cognitiveLevel": "MILD_DEMENTIA",
    "longTermCareGrade": "GRADE_2",
    "notes": "평생 가톨릭 신자로 매일 미사 참례를 원하십니다. 고혈압 약 복용 중입니다.",
    "address": "경기도 고양시 일산동구 중앙로 500",
    "latitude": 37.6584,
    "longitude": 126.7729,
    "preferredTagIds": [1, 5, 18, 33, 47, 48, 53, 79, 80]
  },
  "additionalText": "어머니께서 가톨릭 신앙이 깊으셔서 매일 미사와 기도 시간이 있는 요양원을 찾고 있습니다. 가톨릭 정신을 바탕으로 운영되는 곳이면 더욱 좋겠습니다.",
  "limit": 5
}
```
**태그 설명:**
- 1: 치매 (SPECIALIZATION)
- 5: 고혈압 (SPECIALIZATION)
- 18: 장기요양 (SERVICE)
- 33: 24시간간호사 (OPERATION)
- 47: 정원 (ENVIRONMENT)
- 48: 야외공간 (ENVIRONMENT)
- 53: 예배실 (ENVIRONMENT)
- 79: 존중하는태도 (REVIEW)
- 80: 따뜻한분위기 (REVIEW)

---

## 테스트 사용자 5: 고급 케어 희망 (프리미엄)

프리미엄 케어를 원하는 프로필입니다.

### 예상 매칭 기관:
- **참사랑 요양원** (고급 치매 케어)

### 태그 ID 버전:
```json
{
  "member": {
    "memberId": 5,
    "name": "한보호자"
  },
  "elderlyProfile": {
    "elderlyProfileId": 5,
    "name": "한영숙",
    "gender": "FEMALE",
    "birthDate": "1943-07-10",
    "bloodType": "A",
    "phoneNumber": "010-5678-9012",
    "activityLevel": "LOW",
    "cognitiveLevel": "SEVERE_DEMENTIA",
    "longTermCareGrade": "GRADE_1",
    "notes": "중증 치매로 24시간 집중 케어가 필요합니다. 배회 증상이 있어 안전 시설이 필수입니다.",
    "address": "서울시 강남구 도곡로 400",
    "latitude": 37.4923,
    "longitude": 127.0538,
    "preferredTagIds": [1, 18, 31, 33, 34, 41, 45, 56, 57, 58, 64, 76]
  },
  "additionalText": "어머니께서 중증 치매로 1:3 집중 케어가 필요합니다. 배회 감지 시스템과 안전 시설이 완비된 곳을 찾고 있으며, 가족 상담 프로그램도 있으면 좋겠습니다. 비용보다는 케어의 질이 우선입니다.",
  "limit": 5
}
```
**태그 설명:**
- 1: 치매 (SPECIALIZATION)
- 18: 장기요양 (SERVICE)
- 31: 치매전담 (OPERATION)
- 33: 24시간간호사 (OPERATION)
- 34: 의사상주 (OPERATION)
- 41: 소규모 (OPERATION)
- 45: 개인실 (ENVIRONMENT)
- 56: 의료실 (ENVIRONMENT)
- 57: 응급시스템 (ENVIRONMENT)
- 58: CCTV (ENVIRONMENT)
- 64: 전문적인케어 (REVIEW)
- 76: 개별맞춤케어 (REVIEW)

---

## 전체 태그 ID 참조표

### 전문 질환 (SPECIALIZATION)
- 1: 치매, 2: 뇌졸중, 3: 파킨슨병, 4: 당뇨, 5: 고혈압
- 6: 욕창, 7: 경관영양, 8: 도뇨관, 9: 호흡기질환, 10: 암
- 11: 재활, 12: 정신건강, 13: 완화케어, 14: 골절, 15: 관절염

### 서비스 (SERVICE)
- 16: 주간보호, 17: 단기보호, 18: 장기요양
- 19: 방문요양, 20: 방문간호, 21: 방문목욕, 22: 재가돌봄, 23: 식사배달
- 24: 재활서비스, 25: 의료서비스, 26: 응급돌봄, 27: 휴식돌봄

### 운영 특성 (OPERATION)
- 28: 여성전용, 29: 남성전용, 30: 남녀공용
- 31: 치매전담, 32: 자격증보유직원, 33: 24시간간호사, 34: 의사상주
- 35: 영양사배치, 36: 물리치료사, 37: 주차가능, 38: 셔틀버스
- 39: 반려동물가능, 40: 종교중립, 41: 소규모, 42: 대규모

### 환경 (ENVIRONMENT)
- 43: 엘리베이터, 44: 휠체어접근가능, 45: 개인실, 46: 다인실
- 47: 정원, 48: 야외공간, 49: 운동실, 50: 재활치료실
- 51: 오락실, 52: 도서실, 53: 예배실, 54: 식당, 55: 카페
- 56: 의료실, 57: 응급시스템, 58: CCTV, 59: 화재안전시설
- 60: 냉난방시설, 61: 청결한시설, 62: 신축건물

### 리뷰 (REVIEW)
- 63: 친절한직원, 64: 전문적인케어, 65: 청결함, 66: 음식맛좋음, 67: 다양한메뉴
- 68: 소통잘됨, 69: 신속한대응, 70: 편안한분위기, 71: 좋은프로그램
- 72: 잘관리됨, 73: 합리적인가격, 74: 좋은위치, 75: 가족친화적
- 76: 개별맞춤케어, 77: 응급대응우수, 78: 투명한운영, 79: 존중하는태도
- 80: 따뜻한분위기, 81: 활발한활동, 82: 의료협력우수

---

## 사용 방법

1. **Swagger UI 접속**: `http://localhost:8001/docs`
2. **POST /api/v1/recommendations** 선택
3. **Try it out** 클릭
4. 위의 JSON 중 하나를 복사해서 붙여넣기
5. **Execute** 클릭
6. 응답에서 추천된 기관 리스트 확인

**Note:** Spring에서 태그를 텍스트 배열로 보내는지, ID 배열로 보내는지에 따라 적절한 버전을 사용하세요!
