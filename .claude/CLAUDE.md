# Claude Code Discord Notification Rules

이 규칙은 Claude Code가 작업 완료 시 Discord로 자동 알림을 보내도록 설정합니다.

## 🎯 알림 트리거 시점

Claude Code는 다음 상황에서 Discord 알림을 자동으로 전송해야 합니다:

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

## 📋 일반 규칙

1. **알림은 작업이 완전히 완료된 후에만 전송**
   - 중간 단계에서는 알림을 보내지 않음
   - 모든 파일 저장 및 검증이 완료된 후 전송

2. **프로젝트 이름은 현재 작업 중인 디렉토리명 사용**
   ```python
   import os
   project_name = os.path.basename(os.getcwd())
   ```

3. **메타데이터는 가능한 한 구체적으로 제공**
   - 실행 시간, 처리된 파일 수, 에러 정보 등
   - 사용자가 작업 결과를 바로 이해할 수 있도록

4. **긴 작업(10분 이상)은 진행률 알림 고려**
   - 25%, 50%, 75% 시점에 간단한 진행률 메시지 전송 (선택사항)

5. **에러 발생 시에도 알림 전송**
   - 사용자가 빠르게 문제를 인지할 수 있도록

## 🔧 환경 설정

Discord Webhook URL은 `.env` 파일에서 읽어옵니다:

```python
import os
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
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
notifier.send_notification(
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
