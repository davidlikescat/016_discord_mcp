# 🔔 Claude Code Discord Notifier

Claude Code 작업 완료 시 Discord로 자동 알림을 보내는 MCP 기반 시스템입니다.

## ✨ 주요 기능

- ✅ **작업 완료 알림**: 코딩 작업이 완료되면 자동으로 Discord 알림
- 🏗️ **빌드 완료 알림**: npm run build, 테스트 실행 등 빌드 작업 완료 알림
- ❓ **사용자 의사결정 알림**: 중요한 작업 실행 전 확인이 필요할 때 알림
- 🚨 **에러 알림**: 작업 중 오류 발생 시 즉시 알림
- 📊 **Rich Embed**: Discord Embed 형식으로 깔끔하고 정보가 풍부한 알림

## 📁 프로젝트 구조

```
discord_mcp/
├── README.md                    # 이 파일
├── .env                         # 환경변수 (Webhook URL)
├── requirements.txt             # Python 의존성
├── discord-notify.mcp.json      # MCP 서버 설정
├── .claude/
│   └── CLAUDE.md               # Claude Code 규칙 파일
├── src/
│   └── discord_webhook.py      # Discord Webhook 핸들러
└── examples/                    # 예시 파일 (추후 추가)
```

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
cd discord_mcp
pip install -r requirements.txt
```

### 2. Discord Webhook URL 설정

#### 2.1 Discord에서 Webhook 생성

1. Discord 서버 설정 → **통합 (Integrations)**
2. **Webhooks** → **새 Webhook 생성**
3. Webhook 이름 설정 (예: "Claude Code Notifier")
4. 알림을 받을 채널 선택
5. **Webhook URL 복사**

#### 2.2 .env 파일에 Webhook URL 설정

`.env` 파일은 이미 생성되어 있습니다:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

### 3. 테스트 실행

```bash
cd discord_mcp
python3 src/discord_webhook.py
```

성공적으로 실행되면 Discord 채널에 4개의 테스트 메시지가 전송됩니다:
1. ✅ 작업 완료 알림
2. 🏗️ 빌드 완료 알림
3. ❓ 사용자 의사결정 필요 알림
4. 📨 간단한 메시지

## 📚 사용법

### Python 스크립트에서 직접 사용

```python
from src.discord_webhook import DiscordNotifier
import os
from dotenv import load_dotenv

load_dotenv()

notifier = DiscordNotifier(os.getenv("DISCORD_WEBHOOK_URL"))

# 작업 완료 알림
notifier.send_notification(
    message_type="task_complete",
    project_name="my-project",
    details="FastAPI 백엔드 구현 완료",
    metadata={
        "실행 시간": "3분 45초",
        "생성된 파일": "8개"
    }
)

# 빌드 완료 알림
notifier.send_notification(
    message_type="build_complete",
    project_name="react-frontend",
    details="Production 빌드 완료",
    metadata={
        "빌드 타입": "Production",
        "번들 크기": "2.3MB"
    }
)

# 사용자 의사결정 필요
notifier.send_notification(
    message_type="user_decision",
    project_name="database-migration",
    details="데이터베이스 마이그레이션을 실행하시겠습니까?\n\n• users 테이블 수정\n• 예상 소요 시간: 5-10분",
    metadata={
        "위험도": "중간"
    }
)

# 간단한 메시지
notifier.send_simple_message("🎉 작업이 완료되었습니다!")
```

### Claude Code와 함께 사용

Claude Code가 자동으로 `.claude/CLAUDE.md` 규칙을 참고하여 작업 완료 시 Discord 알림을 전송합니다.

#### Claude Code 실행 시 규칙 적용:

```bash
# Claude Code에 규칙 파일 경로 지정
export CLAUDE_RULES=discord_mcp/.claude/CLAUDE.md
```

또는 프로젝트 root에 `.claude/CLAUDE.md` 파일로 심볼릭 링크 생성:

```bash
ln -s discord_mcp/.claude/CLAUDE.md .claude/CLAUDE.md
```

## 🔧 MCP 서버 설정 (고급)

`discord-notify.mcp.json` 파일은 MCP (Model Context Protocol) 서버 설정을 정의합니다.

```json
{
  "mcpServers": {
    "discord-notifier": {
      "command": "python3",
      "args": ["-m", "src.discord_webhook"],
      "env": {
        "DISCORD_WEBHOOK_URL": "${DISCORD_WEBHOOK_URL}"
      }
    }
  },
  "notifications": {
    "task_complete": { "enabled": true },
    "build_complete": { "enabled": true },
    "user_decision": { "enabled": true },
    "error": { "enabled": true }
  }
}
```

## 📋 알림 타입

### 1. 작업 완료 (task_complete) - 초록색
- 코딩 작업 완료
- 파일 생성/수정 완료
- 리팩토링 완료

### 2. 빌드 완료 (build_complete) - 파란색
- npm run build 완료
- 테스트 실행 완료
- CI/CD 파이프라인 완료

### 3. 사용자 의사결정 (user_decision) - 주황색
- 파일 덮어쓰기 확인
- 데이터베이스 마이그레이션 실행 전 확인
- 중요한 작업 실행 전 확인

### 4. 에러 (error) - 빨간색
- 작업 중 오류 발생
- 빌드 실패
- 테스트 실패

## 🎨 알림 메시지 커스터마이징

`src/discord_webhook.py`의 `DiscordNotifier` 클래스를 수정하여 메시지 형식을 커스터마이징할 수 있습니다.

### Embed 색상 변경:

```python
templates = {
    "task_complete": {
        "title": "✅ 작업 완료!",
        "color": 3066993,  # Green (16진수: 0x2ECC71)
        "emoji": "🎉"
    }
}
```

### 필드 추가:

```python
embed["fields"].append({
    "name": "🔸 커스텀 필드",
    "value": "값",
    "inline": True
})
```

## 🔍 트러블슈팅

### 알림이 전송되지 않음

1. **Webhook URL 확인**:
   ```bash
   cat .env
   ```
   Webhook URL이 올바른지 확인

2. **Discord 서버 권한 확인**:
   - Webhook이 삭제되지 않았는지 확인
   - 채널에 메시지 전송 권한이 있는지 확인

3. **방화벽/네트워크 확인**:
   ```bash
   curl -X POST https://discord.com/api/webhooks/YOUR_WEBHOOK_URL \
     -H "Content-Type: application/json" \
     -d '{"content": "Test message"}'
   ```

### 테스트 스크립트가 실행되지 않음

```bash
# 의존성 재설치
pip install --upgrade -r requirements.txt

# Python 경로 확인
which python3

# 모듈 직접 실행
cd discord_mcp
python3 -m src.discord_webhook
```

## 📝 예시 시나리오

### 시나리오 1: FastAPI 백엔드 구축

```python
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

### 시나리오 2: React 프로덕션 빌드

```python
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

### 시나리오 3: 데이터베이스 마이그레이션 확인

```python
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

## 🤝 기여

이 프로젝트는 001_discord_to_notion 프로젝트의 일부입니다.

## 📄 라이센스

MIT License

## 🔗 관련 링크

- [Discord Webhook Documentation](https://discord.com/developers/docs/resources/webhook)
- [Claude Code Documentation](https://docs.claude.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

**제작**: Claude Code + Discord Integration
**문의**: discord_mcp 폴더 내 이슈 트래커
