# AI 서버 AWS EC2 배포 가이드

## 📋 목차
1. [배포 전 준비사항](#1-배포-전-준비사항)
2. [Docker 이미지 빌드](#2-docker-이미지-빌드)
3. [AWS ECR 설정](#3-aws-ecr-설정)
4. [GitHub Actions CI/CD 구성](#4-github-actions-cicd-구성)
5. [EC2 서버 설정](#5-ec2-서버-설정)
6. [배포 실행](#6-배포-실행)
7. [모니터링 및 트러블슈팅](#7-모니터링-및-트러블슈팅)
8. [스케일 업 가이드](#8-스케일-업-가이드)

---

## 1. 배포 전 준비사항

### 1.1 현재 환경 확인
- **EC2 인스턴스**: t2.micro (1 vCPU, 1GB RAM)
- **Spring Boot**: 8080 포트 사용 중
- **AI 서버**: 8001 포트 사용 예정
- **PostgreSQL**: Spring과 공유 (pgvector 활성화 필요)

### 1.2 필요한 리소스 예상치

| 구성요소 | 메모리 사용량 | 디스크 공간 |
|---------|-------------|-----------|
| Spring Boot | ~500MB | ~200MB |
| AI 서버 (FastAPI) | ~300MB | ~100MB |
| bge-m3 모델 | **~2GB** | **~4GB** |
| PostgreSQL | ~200MB | ~500MB |
| **합계** | **~3GB** | **~5GB** |

⚠️ **경고**: t2.micro는 **1GB RAM**만 제공하므로 **메모리 부족이 예상됩니다.**

### 1.3 해결 방안 우선순위

#### 방안 1: 모델 경량화 (권장 - 비용 절감)
- bge-m3 (1024차원, 2GB) → bge-small-en-v1.5 (384차원, 300MB)
- 정확도는 약간 떨어지지만 속도 개선

#### 방안 2: EC2 스케일 업
- **t2.small** (2GB RAM) - 월 $16.79
- **t3.small** (2GB RAM) - 월 $15.18 (더 나은 성능)

#### 방안 3: AI 서버를 별도 EC2에 분리
- Spring: t2.micro
- AI: t3.small (필요시)

---

## 2. Docker 이미지 빌드

### 2.1 Dockerfile 작성

`ai-server/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# bge-m3 모델 사전 다운로드 (빌드 시간 증가하지만 실행 시 빠름)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8001

# 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 2.2 .dockerignore 작성

```bash
# ai-server/.dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.env
.DS_Store
*.log
.git/
.gitignore
docs/
```

### 2.3 로컬에서 Docker 이미지 테스트

```bash
cd /Users/mychan/Documents/GitHub/caring/caring-ai

# Docker 이미지 빌드
docker build -t caring-ai-server:latest ./ai-server

# 로컬 테스트 (PostgreSQL 연결 정보 수정 필요)
docker run -d \
  --name caring-ai-test \
  -p 8001:8001 \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_NAME=caring \
  -e DB_USER=mychan \
  -e DB_PASSWORD=your_password \
  caring-ai-server:latest

# 로그 확인
docker logs -f caring-ai-test

# 헬스 체크
curl http://localhost:8001/health

# 테스트 완료 후 삭제
docker stop caring-ai-test && docker rm caring-ai-test
```

---

## 3. AWS ECR 설정

### 3.1 ECR 리포지토리 생성

```bash
# AWS CLI로 ECR 리포지토리 생성
aws ecr create-repository \
  --repository-name caring-ai-server \
  --region ap-northeast-2

# 출력 예시:
# {
#     "repository": {
#         "repositoryArn": "arn:aws:ecr:ap-northeast-2:430118840639:repository/caring-ai-server",
#         "repositoryUri": "430118840639.dkr.ecr.ap-northeast-2.amazonaws.com/caring-ai-server"
#     }
# }
```

### 3.2 ECR에 수동 푸시 (테스트용)

```bash
# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin \
  430118840639.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 태그
docker tag caring-ai-server:latest \
  430118840639.dkr.ecr.ap-northeast-2.amazonaws.com/caring-ai-server:latest

# ECR에 푸시
docker push 430118840639.dkr.ecr.ap-northeast-2.amazonaws.com/caring-ai-server:latest
```

---

## 4. GitHub Actions CI/CD 구성

### 4.1 GitHub Secrets 추가

GitHub 리포지토리 > Settings > Secrets and variables > Actions에서 추가:

| Secret 이름 | 값 | 설명 |
|------------|-----|------|
| `AWS_ACCOUNT_ID` | `430118840639` | AWS 계정 ID |
| `AWS_REGION` | `ap-northeast-2` | AWS 리전 |
| `ECR_REPO_AI` | `caring-ai-server` | AI 서버 ECR 리포지토리명 |
| `EC2_HOST` | EC2 퍼블릭 IP | EC2 인스턴스 IP |
| `EC2_USER` | `ubuntu` | EC2 사용자명 |
| `EC2_KEY` | SSH private key | EC2 접속용 Private Key |
| `DB_HOST` | `localhost` | PostgreSQL 호스트 |
| `DB_USER` | DB 사용자명 | PostgreSQL 사용자 |
| `DB_PASSWORD` | DB 비밀번호 | PostgreSQL 비밀번호 |

### 4.2 GitHub Actions Workflow 작성

`.github/workflows/deploy-ai-server.yml`:

```yaml
name: Deploy AI Server to EC2

on:
  push:
    branches: [ "main" ]
    paths:
      - 'ai-server/**'
      - '.github/workflows/deploy-ai-server.yml'
  workflow_dispatch:

env:
  AWS_REGION: ap-northeast-2
  ECR_REPO: caring-ai-server
  IMAGE_URI: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.ap-northeast-2.amazonaws.com/caring-ai-server

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: AWS Role 설정
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::430118840639:role/GitHubActionsECRDeployRole
          aws-region: ${{ secrets.AWS_REGION }}

      - name: ECR에 로그인
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Docker metadata 설정
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_URI }}
          tags: |
            type=raw,value=latest
            type=sha

      - name: Docker Buildx 설정
        uses: docker/setup-buildx-action@v3

      - name: Docker 이미지 빌드 및 ECR에 Push
        uses: docker/build-push-action@v6
        with:
          context: ./ai-server
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64

      - name: EC2 접속 및 배포
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_KEY }}
          script: |
            set -e
            
            # ECR 로그인
            aws ecr get-login-password --region ap-northeast-2 \
              | docker login --username AWS --password-stdin \
              430118840639.dkr.ecr.ap-northeast-2.amazonaws.com
            
            # 기존 컨테이너 중지 및 삭제
            docker stop caring-ai-server || true
            docker rm caring-ai-server || true
            
            # 새 이미지 Pull
            docker pull ${{ env.IMAGE_URI }}:latest
            
            # 새 컨테이너 실행
            docker run -d \
              --name caring-ai-server \
              --restart unless-stopped \
              -p 8001:8001 \
              -e DB_HOST=${{ secrets.DB_HOST }} \
              -e DB_PORT=5432 \
              -e DB_NAME=caring \
              -e DB_USER=${{ secrets.DB_USER }} \
              -e DB_PASSWORD=${{ secrets.DB_PASSWORD }} \
              --network caring-network \
              --log-driver json-file \
              --log-opt max-size=10m \
              --log-opt max-file=3 \
              ${{ env.IMAGE_URI }}:latest
            
            # 구 이미지 정리
            docker image prune -f
            
            # 헬스 체크
            sleep 10
            curl -f http://localhost:8001/health || exit 1
```

---

## 5. EC2 서버 설정

### 5.1 PostgreSQL에 pgvector 확장 설치

```bash
# EC2에 SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# PostgreSQL 접속
sudo -u postgres psql -d caring

# pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

# schema.sql 실행
\i /path/to/caring-ai/database/schema.sql

# 확인
\dx
# vector 확장이 목록에 있어야 함

# 종료
\q
```

### 5.2 Docker Network 생성 (Spring과 공유)

```bash
# caring-network 생성 (이미 있다면 스킵)
docker network create caring-network

# Spring 컨테이너를 네트워크에 연결 (재시작 필요)
docker network connect caring-network caring-server
```

### 5.3 docker-compose.yml 업데이트

기존 `docker-compose.yml`에 AI 서버 추가:

```yaml
services:
  redis:
    # ...existing code...

  caring-server:
    # ...existing code...
    networks:
      - caring-network

  # AI 서버 추가
  caring-ai-server:
    image: 430118840639.dkr.ecr.ap-northeast-2.amazonaws.com/caring-ai-server:latest
    container_name: caring-ai-server
    ports:
      - "8001:8001"
    environment:
      - DB_HOST=host.docker.internal  # 또는 PostgreSQL IP
      - DB_PORT=5432
      - DB_NAME=caring
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
    networks:
      - caring-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  caring-network:
    driver: bridge

volumes:
  redis-data:
```

### 5.4 .env 파일 설정

```bash
# /home/ubuntu/apps/caring/prod/.env
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

---

## 6. 배포 실행

### 6.1 수동 배포 (docker-compose 사용)

```bash
# EC2에서 실행
cd /home/ubuntu/apps/caring/prod

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 \
  | docker login --username AWS --password-stdin \
  430118840639.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 Pull
docker-compose pull caring-ai-server

# 컨테이너 시작
docker-compose up -d caring-ai-server

# 로그 확인
docker-compose logs -f caring-ai-server
```

### 6.2 GitHub Actions로 자동 배포

```bash
# 로컬에서 코드 변경 후 Push
git add .
git commit -m "Deploy AI server"
git push origin main

# GitHub Actions에서 자동으로 배포 진행
# https://github.com/your-repo/actions 에서 확인
```

---

## 7. 모니터링 및 트러블슈팅

### 7.1 헬스 체크

```bash
# 로컬에서
curl http://your-ec2-ip:8001/health

# EC2에서
curl http://localhost:8001/health

# 예상 응답:
# {
#   "status": "healthy",
#   "embedding_service": "loaded",
#   "database": "connected"
# }
```

### 7.2 로그 확인

```bash
# 실시간 로그
docker logs -f caring-ai-server

# 최근 100줄
docker logs --tail 100 caring-ai-server

# 특정 시간 이후 로그
docker logs --since 10m caring-ai-server
```

### 7.3 메모리 사용량 확인

```bash
# 전체 시스템 메모리
free -h

# Docker 컨테이너별 메모리
docker stats caring-ai-server caring-server redis

# 예상 출력:
# CONTAINER          CPU %     MEM USAGE / LIMIT
# caring-ai-server   5.2%      2.1GB / 1GB       ← 문제!
# caring-server      2.1%      500MB / 1GB
# redis              0.5%      50MB / 1GB
```

### 7.4 일반적인 문제 해결

#### 문제 1: 메모리 부족 (OOMKilled)

```bash
# 증상: 컨테이너가 계속 재시작됨
docker ps -a
# STATUS: Exited (137)  ← OOM Killed

# 해결:
# 1. EC2 인스턴스 스케일 업 (섹션 8 참조)
# 2. 또는 경량 모델 사용 (아래 참조)
```

**경량 모델로 변경**:

```python
# ai-server/services/embedding_service.py 수정
# self.model = SentenceTransformer('BAAI/bge-m3')  # 2GB
self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')  # 300MB
```

```dockerfile
# Dockerfile 수정
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"
```

#### 문제 2: DB 연결 실패

```bash
# 로그 확인
docker logs caring-ai-server | grep "DB 연결 실패"

# PostgreSQL 접속 테스트
docker exec -it caring-ai-server python -c "
import psycopg2
conn = psycopg2.connect(
    host='host.docker.internal',
    port=5432,
    database='caring',
    user='mychan',
    password='your_password'
)
print('연결 성공')
"

# 해결:
# 1. .env 파일의 DB 정보 확인
# 2. PostgreSQL이 외부 접속 허용하는지 확인
#    - postgresql.conf: listen_addresses = '*'
#    - pg_hba.conf: host all all 0.0.0.0/0 md5
```

#### 문제 3: 포트 충돌

```bash
# 8001 포트 사용 중인 프로세스 확인
sudo lsof -i :8001

# 해결: 다른 포트 사용
docker run -d -p 8002:8001 ...
```

---

## 8. 스케일 업 가이드

### 8.1 t2.micro → t2.small 업그레이드

**비용**: 월 $16.79 (약 ₩22,000)

**절차**:

1. **EC2 인스턴스 중지**

```bash
# AWS Console 또는 CLI
aws ec2 stop-instances --instance-ids i-your-instance-id
```

2. **인스턴스 타입 변경**

```bash
aws ec2 modify-instance-attribute \
  --instance-id i-your-instance-id \
  --instance-type "{\"Value\": \"t2.small\"}"
```

3. **인스턴스 시작**

```bash
aws ec2 start-instances --instance-ids i-your-instance-id
```

4. **서비스 재시작**

```bash
ssh ubuntu@your-ec2-ip

cd /home/ubuntu/apps/caring/prod
docker-compose up -d
```

### 8.2 t3.small로 업그레이드 (권장)

**비용**: 월 $15.18 (약 ₩20,000)  
**장점**: t2보다 **40% 더 나은 성능**, 버스트 크레딧 무제한

```bash
# t3.small로 변경
aws ec2 modify-instance-attribute \
  --instance-id i-your-instance-id \
  --instance-type "{\"Value\": \"t3.small\"}"
```

### 8.3 Swap 메모리 추가 (임시 해결책)

메모리 부족 시 디스크를 RAM처럼 사용 (성능 저하 있음):

```bash
# 2GB Swap 파일 생성
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 확인
free -h
```

### 8.4 AI 서버를 별도 EC2로 분리

**구성**:
- **EC2-1** (Spring): t2.micro - 월 $8.50
- **EC2-2** (AI): t3.small - 월 $15.18
- **총 비용**: 월 $23.68 (약 ₩31,000)

**장점**:
- Spring과 AI 서버 독립적으로 스케일링
- 장애 격리
- 더 나은 성능

---

## 9. 배포 체크리스트

### 배포 전

- [ ] PostgreSQL에 pgvector 확장 설치 확인
- [ ] schema.sql 실행 완료
- [ ] ECR 리포지토리 생성
- [ ] GitHub Secrets 설정
- [ ] .env 파일 준비
- [ ] 로컬에서 Docker 이미지 테스트

### 배포 중

- [ ] GitHub Actions 워크플로우 실행 확인
- [ ] ECR에 이미지 푸시 성공 확인
- [ ] EC2에서 컨테이너 실행 확인
- [ ] 헬스 체크 통과 확인

### 배포 후

- [ ] `/health` 엔드포인트 확인
- [ ] Swagger UI 접속 확인 (`http://ec2-ip:8001/docs`)
- [ ] 기관 등록 API 테스트
- [ ] 추천 API 테스트
- [ ] 로그 모니터링 설정
- [ ] 메모리 사용량 모니터링

---

## 10. 유용한 명령어 모음

```bash
# 전체 컨테이너 상태 확인
docker ps -a

# 특정 컨테이너 재시작
docker restart caring-ai-server

# 로그 스트리밍
docker logs -f caring-ai-server

# 컨테이너 내부 접속
docker exec -it caring-ai-server /bin/bash

# 메모리 및 CPU 사용량
docker stats

# 불필요한 이미지 정리
docker image prune -a

# 전체 시스템 정리 (주의!)
docker system prune -a --volumes

# EC2 디스크 사용량 확인
df -h

# PostgreSQL 테이블 크기 확인
sudo -u postgres psql -d caring -c "
SELECT 
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

---

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Docker 공식 문서](https://docs.docker.com/)
- [AWS ECR 문서](https://docs.aws.amazon.com/ecr/)
- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [pgvector 문서](https://github.com/pgvector/pgvector)
