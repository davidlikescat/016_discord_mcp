# GCP Cloud Run 배포 가이드

[English Version](GCP_DEPLOY_EN.md)

## 개요

이 가이드는 Discord MCP Notifier를 Google Cloud Platform(GCP)의 Cloud Run에 배포하는 방법을 설명합니다.

## 왜 Cloud Run?

- **서버리스**: 서버 관리 불필요
- **자동 스케일링**: 트래픽에 따라 자동으로 확장/축소
- **비용 효율적**: 사용한 만큼만 지불 (무료 티어 제공)
- **HTTPS 자동 설정**: SSL 인증서 자동 관리
- **컨테이너 기반**: Docker를 사용한 표준화된 배포

## 📋 사전 요구사항

1. **GCP 계정** 생성
   - https://cloud.google.com/
   - 무료 크레딧 $300 제공 (신규 가입 시)

2. **GCP 프로젝트** 생성
   - GCP Console에서 새 프로젝트 생성
   - 프로젝트 ID 기억하기 (예: `discord-mcp-notifier`)

3. **gcloud CLI** 설치
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Ubuntu/Debian
   curl https://sdk.cloud.google.com | bash

   # Windows
   # https://cloud.google.com/sdk/docs/install 참고
   ```

4. **Docker** 설치
   ```bash
   # macOS
   brew install docker

   # Ubuntu/Debian
   sudo apt-get install docker.io

   # Windows
   # https://docs.docker.com/desktop/install/windows-install/
   ```

## 🚀 배포 단계

### 1. gcloud CLI 인증

```bash
# Google 계정으로 로그인
gcloud auth login

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# 예시:
# gcloud config set project discord-mcp-notifier
```

### 2. API 활성화

```bash
# Cloud Run API 활성화
gcloud services enable run.googleapis.com

# Container Registry API 활성화
gcloud services enable containerregistry.googleapis.com

# Artifact Registry API 활성화 (권장)
gcloud services enable artifactregistry.googleapis.com
```

### 3. Docker 이미지 빌드

```bash
# 프로젝트 디렉토리로 이동
cd /path/to/016_discord_mcp

# Docker 이미지 빌드
docker build -t discord-mcp-notifier .

# 빌드 확인
docker images | grep discord-mcp-notifier
```

### 4. Docker 이미지를 GCP에 푸시

#### 방법 1: Artifact Registry 사용 (권장)

```bash
# Artifact Registry 저장소 생성
gcloud artifacts repositories create discord-mcp \
  --repository-format=docker \
  --location=asia-northeast3 \
  --description="Discord MCP Notifier"

# Docker 인증 설정
gcloud auth configure-docker asia-northeast3-docker.pkg.dev

# 이미지 태그
docker tag discord-mcp-notifier \
  asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:latest

# 이미지 푸시
docker push asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:latest
```

#### 방법 2: Container Registry 사용 (레거시)

```bash
# Docker 인증 설정
gcloud auth configure-docker

# 이미지 태그
docker tag discord-mcp-notifier gcr.io/YOUR_PROJECT_ID/discord-mcp-notifier:latest

# 이미지 푸시
docker push gcr.io/YOUR_PROJECT_ID/discord-mcp-notifier:latest
```

### 5. Secret Manager에 Webhook URL 저장

```bash
# Secret Manager API 활성화
gcloud services enable secretmanager.googleapis.com

# Secret 생성
echo -n "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL" | \
  gcloud secrets create discord-webhook-url \
    --data-file=-

# Secret 확인
gcloud secrets describe discord-webhook-url
```

### 6. Cloud Run 서비스 배포

#### Artifact Registry 사용 시:

```bash
gcloud run deploy discord-mcp-notifier \
  --image asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:latest \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-secrets DISCORD_WEBHOOK_URL=discord-webhook-url:latest \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 60
```

#### Container Registry 사용 시:

```bash
gcloud run deploy discord-mcp-notifier \
  --image gcr.io/YOUR_PROJECT_ID/discord-mcp-notifier:latest \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-secrets DISCORD_WEBHOOK_URL=discord-webhook-url:latest \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 60
```

**옵션 설명:**
- `--platform managed`: 완전 관리형 Cloud Run 사용
- `--region asia-northeast3`: 서울 리전 (한국)
- `--allow-unauthenticated`: 인증 없이 접근 허용 (공개 API)
- `--set-secrets`: Secret Manager에서 환경 변수 주입
- `--memory 256Mi`: 메모리 256MB 할당
- `--cpu 1`: CPU 1개 할당
- `--max-instances 10`: 최대 인스턴스 10개
- `--min-instances 0`: 최소 인스턴스 0개 (비용 절약)
- `--timeout 60`: 요청 타임아웃 60초

### 7. 배포 확인

배포가 완료되면 Cloud Run이 서비스 URL을 제공합니다:

```
Service [discord-mcp-notifier] revision [discord-mcp-notifier-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://discord-mcp-notifier-XXXX-an.a.run.app
```

#### 헬스체크 테스트:

```bash
curl https://discord-mcp-notifier-XXXX-an.a.run.app/

# 응답:
# {"status":"healthy","service":"discord-mcp-notifier"}
```

#### 알림 전송 테스트:

```bash
curl -X POST https://discord-mcp-notifier-XXXX-an.a.run.app/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "task_complete",
    "project_name": "GCP Deployment Test",
    "details": "Cloud Run 배포 성공!",
    "metadata": {
      "Region": "asia-northeast3",
      "Memory": "256Mi"
    }
  }'

# 응답:
# {"status":"success"}
```

## 🔄 업데이트 및 재배포

코드를 수정한 후 재배포하는 방법:

```bash
# 1. Docker 이미지 다시 빌드
docker build -t discord-mcp-notifier .

# 2. 이미지 태그 (버전 번호 변경)
docker tag discord-mcp-notifier \
  asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:v1.1

# 3. 이미지 푸시
docker push asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:v1.1

# 4. Cloud Run 서비스 업데이트
gcloud run deploy discord-mcp-notifier \
  --image asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/discord-mcp/notifier:v1.1 \
  --platform managed \
  --region asia-northeast3
```

## 📊 모니터링 및 로그

### 로그 확인

```bash
# 실시간 로그 스트리밍
gcloud run services logs tail discord-mcp-notifier \
  --region asia-northeast3 \
  --follow

# 최근 로그 조회
gcloud run services logs read discord-mcp-notifier \
  --region asia-northeast3 \
  --limit 50
```

### GCP Console에서 모니터링

1. GCP Console → Cloud Run
2. `discord-mcp-notifier` 서비스 클릭
3. **Metrics** 탭: 요청 수, 응답 시간, 에러율 등 확인
4. **Logs** 탭: 상세 로그 확인
5. **Revisions** 탭: 배포 이력 및 버전 관리

## 💰 비용 최적화

### 무료 티어 (Free Tier)

Cloud Run은 다음과 같은 무료 사용량을 제공합니다 (월별):

- **CPU**: 180,000 vCPU-초
- **메모리**: 360,000 GiB-초
- **요청**: 2백만 건
- **네트워크 이그레스**: 1 GB (북미 리전)

### 비용 절감 팁

1. **최소 인스턴스 0으로 설정**: 사용하지 않을 때 과금 없음
2. **메모리 최적화**: 필요한 만큼만 할당 (256Mi면 충분)
3. **타임아웃 설정**: 불필요하게 긴 타임아웃 방지
4. **리전 선택**: 가까운 리전 선택 (asia-northeast3)

### 예상 비용 계산

**시나리오**: 하루 100번 알림 전송 (월 3,000건)

- **요청 수**: 3,000건 → 무료 (2백만 건 이내)
- **CPU/메모리**: 요청당 ~1초 실행 → 무료 (180,000초 이내)
- **네트워크**: 거의 무시 가능 → 무료

**결론**: 대부분의 개인/소규모 프로젝트는 무료 티어 내에서 운영 가능!

## 🔒 보안 설정

### 1. 인증 추가 (선택사항)

공개 API가 아닌 인증된 요청만 허용하려면:

```bash
# 인증 필요로 변경
gcloud run services update discord-mcp-notifier \
  --region asia-northeast3 \
  --no-allow-unauthenticated

# 서비스 계정에 권한 부여
gcloud run services add-iam-policy-binding discord-mcp-notifier \
  --region asia-northeast3 \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### 2. API Key 추가 (선택사항)

간단한 API Key 인증을 추가하려면 코드 수정:

```python
# app.py에 추가
import os

API_KEY = os.getenv("API_KEY", "your-secret-api-key")

@app.before_request
def check_api_key():
    if request.endpoint != 'health_check':
        api_key = request.headers.get("X-API-Key")
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
```

Secret Manager에 API Key 추가:

```bash
echo -n "your-secret-api-key" | \
  gcloud secrets create api-key \
    --data-file=-

# 서비스 업데이트
gcloud run deploy discord-mcp-notifier \
  --set-secrets API_KEY=api-key:latest \
  --update-secrets DISCORD_WEBHOOK_URL=discord-webhook-url:latest
```

## 🧪 CI/CD 파이프라인 (선택사항)

GitHub Actions를 사용한 자동 배포:

`.github/workflows/deploy.yml` 파일 생성:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

env:
  PROJECT_ID: YOUR_PROJECT_ID
  SERVICE_NAME: discord-mcp-notifier
  REGION: asia-northeast3

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ env.PROJECT_ID }}

    - name: Configure Docker
      run: gcloud auth configure-docker asia-northeast3-docker.pkg.dev

    - name: Build Docker image
      run: docker build -t asia-northeast3-docker.pkg.dev/$PROJECT_ID/discord-mcp/notifier:$GITHUB_SHA .

    - name: Push Docker image
      run: docker push asia-northeast3-docker.pkg.dev/$PROJECT_ID/discord-mcp/notifier:$GITHUB_SHA

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy $SERVICE_NAME \
          --image asia-northeast3-docker.pkg.dev/$PROJECT_ID/discord-mcp/notifier:$GITHUB_SHA \
          --platform managed \
          --region $REGION \
          --allow-unauthenticated
```

## 🔍 트러블슈팅

### 문제 1: "Permission denied" 에러

```bash
# 서비스 계정에 필요한 권한 부여
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

### 문제 2: Docker 이미지 푸시 실패

```bash
# Docker 인증 재설정
gcloud auth configure-docker asia-northeast3-docker.pkg.dev

# 로그인 확인
gcloud auth list
```

### 문제 3: Secret 접근 불가

```bash
# 서비스 계정에 Secret 접근 권한 부여
gcloud secrets add-iam-policy-binding discord-webhook-url \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 📞 지원

- **GCP 문서**: https://cloud.google.com/run/docs
- **GitHub Issues**: https://github.com/davidlikescat/016_discord_mcp/issues
- **Discord 커뮤니티**: (추가 예정)

---

**작성**: Discord MCP Notifier 프로젝트
**날짜**: 2025-10-27
