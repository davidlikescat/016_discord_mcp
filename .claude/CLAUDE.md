# Claude Code Discord Notification Rules

## ⚠️ 필수 규칙: 모든 응답 전에 Discord 알림!

**Claude Code는 사용자에게 응답하기 전에 반드시 Discord 알림을 먼저 보내야 합니다.**

## 🎯 핵심 원칙: 사용자를 기다리게 하지 마라!

**작업을 완료했거나, 질문을 하거나, 사용자 응답이 필요한 순간 = 즉시 Discord 알림!**

### 알림을 보내는 방법:

```bash
curl -X POST https://discord-mcp-notifier-1012585134222.asia-northeast3.run.app/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "task_complete/user_decision/build_complete/error",
    "project_name": "현재 프로젝트명",
    "details": "사용자에게 전달할 메시지",
    "metadata": {
      "대기 중": "사용자 응답/다음 명령",
      "다음 액션": "구체적인 액션"
    }
  }'
```

### 📱 필수 동작 흐름:

1. **작업 완료** → Discord 알림 전송 → 사용자에게 완료 메시지
2. **질문 필요** → Discord 알림 전송 → 사용자에게 질문
3. **에러 발생** → Discord 알림 전송 → 사용자에게 에러 보고
4. **긴 작업 완료** → Discord 알림 전송 → 사용자에게 결과 보고

## 🎯 알림 트리거 시점 (필수)

Claude Code는 다음 상황에서 Discord 알림을 **반드시** 자동으로 전송해야 합니다:

### 1. 작업 완료 (Task Complete)
- 사용자가 요청한 코딩 작업이 완료되었을 때
- 파일 생성/수정/삭제 작업이 모두 완료되었을 때
- 리팩토링, 버그 수정 등이 완료되었을 때

**알림 방법:**
```python
from src.discord_webhook import DiscordNotifier
notifier = DiscordNotifier(WEBHOOK_URL)
notifier.send_notification(
    message_type="task_complete",
    project_name="프로젝트명",
    details="작업 내용 요약",
    metadata={
        "실행 시간": "소요 시간",
        "처리된 파일": "파일 개수"
    }
)
```

### 2. 빌드 완료 (Build Complete)
- `npm run build`, `python setup.py build` 등 빌드 명령이 성공적으로 완료되었을 때
- CI/CD 파이프라인 실행이 완료되었을 때
- 테스트 실행이 완료되었을 때

**알림 방법:**
```python
notifier.send_notification(
    message_type="build_complete",
    project_name="프로젝트명",
    details="빌드 타입 및 결과",
    metadata={
        "빌드 타입": "production/development",
        "번들 크기": "크기",
        "테스트 결과": "pass/fail"
    }
)
```

### 3. 사용자 의사결정 필요 (User Decision Required)
- 파일 덮어쓰기, 삭제 등 중요한 작업 전 확인이 필요할 때
- 데이터베이스 마이그레이션 등 위험한 작업 실행 전
- 여러 옵션 중 선택이 필요할 때

**알림 방법:**
```python
notifier.send_notification(
    message_type="user_decision",
    project_name="프로젝트명",
    details="확인이 필요한 작업 설명\n\n• 옵션 1\n• 옵션 2",
    metadata={
        "작업 타입": "파일 삭제/마이그레이션 등",
        "위험도": "낮음/중간/높음"
    }
)
```

### 4. 에러 발생 (Error)
- 작업 중 오류가 발생했을 때
- 빌드 실패, 테스트 실패 등

**알림 방법:**
```python
notifier.send_notification(
    message_type="error",
    project_name="프로젝트명",
    details="에러 메시지 및 스택 트레이스",
    metadata={
        "에러 타입": "SyntaxError/RuntimeError 등",
        "발생 위치": "파일명:라인"
    }
)
```

### 5. 사용자 입력 대기 중 (User Action Required) ⭐ 중요!
- **사용자에게 질문하거나 확인을 요청할 때**
- **사용자가 설정해야 할 것이 있을 때**
- **사용자가 외부에서 작업해야 할 때** (예: GitHub 저장소 생성, API 키 발급 등)
- **다음 단계를 진행하기 전에 사용자 응답이 필요할 때**

**예시:**
- "GitHub 저장소 URL을 알려주세요"
- "Discord Webhook URL을 설정해야 합니다"
- "Docker를 설치해야 합니다"
- "GCP 프로젝트 ID를 입력해주세요"
- "브라우저에서 인증을 완료해주세요"

**알림 방법:**
```python
notifier.send_notification(
    message_type="user_decision",
    project_name="프로젝트명",
    details="사용자가 해야 할 작업 설명\n\n예: GitHub에서 저장소를 생성하고 URL을 알려주세요",
    metadata={
        "대기 중": "사용자 응답",
        "다음 단계": "구체적인 액션"
    }
)
```

### 6. 진행 상황 업데이트 (Progress Update)
- 긴 작업(1분 이상) 진행 중일 때
- 중요한 단계가 완료되었을 때
- 사용자가 진행 상황을 알아야 할 때

**알림 방법:**
```python
notifier.send_notification(
    message_type="build_complete",
    project_name="프로젝트명",
    details="현재 진행 중: Docker 이미지 빌드 중...",
    metadata={
        "진행률": "50%",
        "예상 시간": "1분 남음"
    }
)
```

## 📋 일반 규칙 (반드시 준수)

### ⭐ 가장 중요한 규칙:
**사용자가 다음 액션을 취해야 하는 순간 = 즉시 Discord 알림 전송!**

### 🚨 필수 체크리스트 (모든 응답 전에 확인):

- [ ] 작업을 완료했는가? → Discord 알림 전송
- [ ] 사용자에게 질문하는가? → Discord 알림 전송
- [ ] 사용자 응답을 기다리는가? → Discord 알림 전송
- [ ] 에러가 발생했는가? → Discord 알림 전송
- [ ] 사용자가 다음에 뭔가 해야 하는가? → Discord 알림 전송

**위 항목 중 하나라도 해당하면 반드시 curl 명령어로 Discord 알림을 보낸 후 응답하세요!**

### 알림 전송 예시:

```bash
# 예시 1: 작업 완료 시
curl -X POST https://discord-mcp-notifier-1012585134222.asia-northeast3.run.app/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "task_complete",
    "project_name": "016_discord_mcp",
    "details": "작업이 완료되었습니다!\n\n완료된 내용을 확인해주세요.",
    "metadata": {
      "대기 중": "사용자 다음 명령"
    }
  }'

# 예시 2: 질문 시
curl -X POST https://discord-mcp-notifier-1012585134222.asia-northeast3.run.app/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "user_decision",
    "project_name": "016_discord_mcp",
    "details": "⏸️ 사용자 응답이 필요합니다!\n\n질문: GitHub 저장소 URL을 입력해주세요.",
    "metadata": {
      "대기 중": "사용자 응답",
      "다음 액션": "URL 입력"
    }
  }'
```

1. **사용자 입력 대기 시 무조건 알림 전송**
   - 질문하기 전에 먼저 Discord 알림 전송
   - 사용자가 터미널을 보지 않아도 Discord에서 확인 가능
   - 예: "GitHub 저장소 URL을 입력해주세요" → Discord 알림 먼저 전송

2. **작업 완료 시 항상 알림 전송**
   - 모든 파일 저장 및 검증이 완료된 후 전송
   - 사용자가 다음에 무엇을 해야 하는지 명확히 안내

3. **프로젝트 이름은 현재 작업 중인 디렉토리명 사용**
   ```python
   import os
   project_name = os.path.basename(os.getcwd())
   ```

4. **메타데이터는 가능한 한 구체적으로 제공**
   - 실행 시간, 처리된 파일 수, 에러 정보 등
   - 사용자가 작업 결과를 바로 이해할 수 있도록
   - **다음 액션이 무엇인지 반드시 포함**

5. **긴 작업(1분 이상)은 진행률 알림 필수**
   - 작업 시작 시 알림
   - 50% 완료 시 알림
   - 작업 완료 시 알림
   - 사용자가 대기 시간을 알 수 있도록

6. **에러 발생 시에도 즉시 알림 전송**
   - 사용자가 빠르게 문제를 인지할 수 있도록
   - 해결 방법도 함께 안내

## 🔧 환경 설정

### 방법 1: 로컬에서 직접 실행 (개발 환경)

Discord Webhook URL은 `.env` 파일에서 읽어옵니다:

```python
import os
from dotenv import load_dotenv
from src.discord_webhook import DiscordNotifier

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
notifier = DiscordNotifier(WEBHOOK_URL)
```

### 방법 2: GCP Cloud Run API 사용 (프로덕션) ⭐ 권장

**이미 배포된 Cloud Run 서비스를 사용하세요!**

```python
import requests
import os

# GCP Cloud Run 서비스 URL
CLOUD_RUN_URL = "https://discord-mcp-notifier-1012585134222.asia-northeast3.run.app/notify"

def send_discord_notification(message_type, project_name, details, metadata):
    """GCP Cloud Run을 통해 Discord 알림 전송"""
    try:
        response = requests.post(
            CLOUD_RUN_URL,
            json={
                "message_type": message_type,
                "project_name": project_name,
                "details": details,
                "metadata": metadata
            },
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ Discord 알림 전송 성공: {message_type}")
            return True
        else:
            print(f"❌ Discord 알림 전송 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Discord 알림 전송 오류: {e}")
        return False

# 사용 예시
project_name = os.path.basename(os.getcwd())
send_discord_notification(
    message_type="task_complete",
    project_name=project_name,
    details="작업 완료!",
    metadata={"상태": "SUCCESS"}
)
```

## 예시 시나리오

### 시나리오 1: FastAPI 백엔드 구축 완료
```python
# 모든 파일 생성 및 수정 완료 후
from src.discord_webhook import DiscordNotifier

notifier = DiscordNotifier(os.getenv("DISCORD_WEBHOOK_URL"))
notifier.send_notification(
    message_type="task_complete",
    project_name="fastapi-backend",
    details="FastAPI 백엔드 구조 생성 완료\n\n• API 엔드포인트 5개 생성\n• 데이터베이스 모델 정의\n• 인증 미들웨어 구현",
    metadata={
        "실행 시간": "3분 45초",
        "생성된 파일": "8개",
        "코드 라인": "~450줄"
    }
)
```

### 시나리오 2: 프로덕션 빌드 완료
```python
# npm run build 완료 후
notifier.send_notification(
    message_type="build_complete",
    project_name="react-frontend",
    details="Production 빌드 완료 및 최적화 성공",
    metadata={
        "빌드 타입": "Production",
        "번들 크기": "2.3MB (gzip: 780KB)",
        "빌드 시간": "1분 23초"
    }
)
```

### 시나리오 3: 데이터베이스 마이그레이션 확인 필요
```python
# 마이그레이션 실행 전
send_discord_notification(
    message_type="user_decision",
    project_name="database-migration",
    details="다음 마이그레이션을 실행하시겠습니까?\n\n• users 테이블에 email_verified 컬럼 추가\n• posts 테이블 인덱스 재구성\n• 예상 소요 시간: 5-10분",
    metadata={
        "마이그레이션 파일": "20251027_add_email_verification.sql",
        "영향받는 테이블": "users, posts",
        "위험도": "중간"
    }
)
```

### 시나리오 4: 사용자 입력 필요 ⭐ 가장 중요!
```python
# 사용자에게 GitHub 저장소 URL을 물어보기 전에 먼저 Discord 알림 전송
send_discord_notification(
    message_type="user_decision",
    project_name=os.path.basename(os.getcwd()),
    details="⏸️ 사용자 입력이 필요합니다!\n\nGitHub 저장소 URL을 입력해주세요.\n\n예시: https://github.com/username/repo-name",
    metadata={
        "대기 중": "GitHub 저장소 URL",
        "다음 액션": "터미널에 URL 입력",
        "상태": "입력 대기 중..."
    }
)

# 그 다음에 사용자에게 질문
github_url = input("GitHub 저장소 URL을 입력하세요: ")
```

### 시나리오 5: Docker 설치 필요
```python
# Docker가 없을 때
send_discord_notification(
    message_type="user_decision",
    project_name=os.path.basename(os.getcwd()),
    details="⚠️ Docker가 설치되어 있지 않습니다!\n\n다음 중 하나를 선택해주세요:\n\n1. Docker Desktop 설치 (https://www.docker.com/products/docker-desktop)\n2. Cloud Build 사용 (Docker 없이 GCP에서 빌드)\n\n터미널에서 선택해주세요!",
    metadata={
        "필요한 것": "Docker 또는 대안 선택",
        "옵션 1": "Docker Desktop 설치",
        "옵션 2": "Cloud Build 사용",
        "대기 중": "사용자 선택"
    }
)

# 사용자에게 선택 요청
print("\n1. Docker 설치하기")
print("2. Cloud Build 사용하기")
choice = input("선택하세요 (1/2): ")
```

### 시나리오 6: GCP 배포 완료 후 테스트 필요
```python
# 배포 완료 후
send_discord_notification(
    message_type="task_complete",
    project_name=os.path.basename(os.getcwd()),
    details="🎉 GCP Cloud Run 배포 완료!\n\n✅ 서비스 URL: https://your-service.run.app\n✅ 헬스체크 통과\n✅ Secret Manager 설정 완료\n\n다음 액션: Discord 채널에서 테스트 알림을 확인하세요!",
    metadata={
        "서비스 URL": "https://your-service.run.app",
        "상태": "ACTIVE",
        "다음 액션": "Discord에서 알림 확인",
        "테스트 방법": "curl 명령어 제공됨"
    }
)
```

## 🚀 사용법

1. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

2. `.env` 파일 설정:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
   ```

3. Claude Code가 자동으로 이 규칙을 따라 알림 전송

---

**참고:** 이 규칙 파일은 Claude Code가 작업 수행 시 참고하는 가이드라인입니다. 실제 MCP 연동이 필요한 경우 `discord-notify.mcp.json` 파일도 함께 설정해야 합니다.
