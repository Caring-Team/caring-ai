-- 테스트용 더미 테이블 및 데이터

-- 기관 테이블
CREATE TABLE IF NOT EXISTS institutions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- '재활병원', '요양센터', '복지관'
    address TEXT NOT NULL,
    description TEXT,
    services TEXT[],  -- 서비스 배열
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 보호자 테이블
CREATE TABLE IF NOT EXISTS guardians (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT,
    region VARCHAR(255),
    preferences TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- 어르신 테이블
CREATE TABLE IF NOT EXISTS seniors (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    age INT,
    gender VARCHAR(10),
    diseases TEXT[],
    care_level VARCHAR(50),
    required_services TEXT[],
    special_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 테스트 기관 데이터 삽입
INSERT INTO institutions (name, type, address, description, services) VALUES
('서울재활병원', '재활병원', '서울특별시 강남구 테헤란로 123', '전문 재활 서비스를 제공하는 종합 의료 기관', 
    ARRAY['재활치료', '물리치료', '운동치료', '당뇨관리', '고혈압관리']),
('건강증진센터', '요양센터', '서울특별시 서초구 서초대로 456', '예방의학 중심의 건강증진 서비스', 
    ARRAY['건강검진', '영양상담', '운동프로그램', '만성질환관리']),
('노인복지관', '복지관', '서울특별시 강남구 봉은사로 789', '어르신들을 위한 종합 복지 서비스', 
    ARRAY['노인복지', '여가활동', '사회활동', '건강관리', '식사지원']),
('당뇨병센터', '재활병원', '서울특별시 송파구 올림픽로 321', '당뇨병 전문 치료 및 관리 프로그램', 
    ARRAY['당뇨병', '혈당관리', '식이요법', '운동치료', '합병증예방']),
('심혈관질환센터', '요양센터', '서울특별시 강남구 강남대로 654', '심혈관 질환 전문 진료 및 예방', 
    ARRAY['심장질환', '고혈압', '고지혈증', '심전도검사', '운동부하검사'])
ON CONFLICT DO NOTHING;

-- 테스트 보호자 데이터
INSERT INTO guardians (member_id, region, preferences) VALUES
(1, '서울특별시 강남구', ARRAY['깨끗한 시설', '친절한 직원', '가까운 거리']),
(2, '서울특별시 서초구', ARRAY['전문 의료진', '재활 프로그램'])
ON CONFLICT DO NOTHING;

-- 테스트 어르신 데이터
INSERT INTO seniors (name, age, gender, diseases, care_level, required_services, special_notes) VALUES
('김철수', 75, '남성', ARRAY['당뇨병', '고혈압'], '3등급', ARRAY['재활치료', '물리치료', '운동치료'], '낙상 위험 있음'),
('이영희', 82, '여성', ARRAY['치매', '관절염'], '2등급', ARRAY['인지치료', '물리치료'], '거동 불편'),
('박민수', 68, '남성', ARRAY['당뇨병'], '4등급', ARRAY['당뇨관리', '식이요법'], '식이 조절 필요')
ON CONFLICT DO NOTHING;

-- 확인 쿼리
SELECT 'institutions' as table_name, COUNT(*) as count FROM institutions
UNION ALL
SELECT 'guardians', COUNT(*) FROM guardians
UNION ALL
SELECT 'seniors', COUNT(*) FROM seniors;
