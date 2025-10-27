# MCP (Model Context Protocol) 상세 설명

## MCP란?

**MCP (Model Context Protocol)**은 AI 모델(예: Claude)과 외부 시스템/도구를 연결하는 표준화된 프로토콜입니다. 이를 통해 AI가 특정 기능(파일 시스템 접근, 데이터베이스 쿼리, API 호출 등)을 안전하고 구조화된 방식으로 실행할 수 있습니다.

### 핵심 개념

- **프로토콜**: AI와 외부 도구 간의 통신 규약
- **서버**: 특정 기능을 제공하는 독립적인 프로세스 (예: Discord 알림 전송)
- **클라이언트**: AI 모델 (Claude Code)이 MCP 서버와 통신하는 인터페이스
- **도구(Tools)**: MCP 서버가 제공하는 개별 기능들

---

## 이 프로젝트에서의 MCP 역할

### 1. 아키텍처 개요

```
┌─────────────────────┐
│   Claude Code       │  ← AI 모델 (클라이언트)
│   (AI Assistant)    │
└──────────┬──────────┘
           │
           │ MCP Protocol
           │
┌──────────▼──────────────────────────────────┐
│   MCP Server (discord-notifier)             │
│   - discord-notify.mcp.json (설정)          │
│   - src/discord_webhook.py (구현)           │
└──────────┬──────────────────────────────────┘
           │
           │ HTTP Webhook
           │
┌──────────▼──────────┐
│   Discord API       │  ← 최종 목적지
│   (Webhook)         │
└─────────────────────┘
```

### 2. 동작 흐름

1. **Claude Code가 작업 완료를 감지**
   - 예: 파일 생성/수정 완료, 빌드 완료, 에러 발생 등

2. **Claude Code가 MCP 서버 호출**
   - `.claude/CLAUDE.md` 규칙에 따라 MCP 서버 실행 트리거
   - `discord-notify.mcp.json` 설정 파일 참조

3. **MCP 서버 실행**
   ```bash
   python3 -m src.discord_webhook
   ```
   - `discord-notify.mcp.json`의 `command`와 `args` 사용

4. **Discord Webhook으로 알림 전송**
   - `DiscordNotifier` 클래스가 HTTP POST 요청 전송
   - Embed 형식의 풍부한 알림 메시지 생성

5. **Discord 채널에 메시지 표시**
   - 사용자가 설정한 채널에 실시간 알림 도착

---

## MCP 설정 파일: `discord-notify.mcp.json`

### 전체 구조

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
    "task_complete": {
      "enabled": true,
      "message_type": "task_complete"
    },
    "build_complete": {
      "enabled": true,
      "message_type": "build_complete"
    },
    "user_decision": {
      "enabled": true,
      "message_type": "user_decision"
    },
    "error": {
      "enabled": true,
      "message_type": "error"
    }
  }
}
```

### 각 섹션 설명

#### 1. `mcpServers` 섹션

MCP 서버의 실행 방법을 정의합니다.

```json
"mcpServers": {
  "discord-notifier": {  // ← 서버 이름 (사용자 정의)
    "command": "python3",  // ← 실행할 명령어
    "args": ["-m", "src.discord_webhook"],  // ← 명령어 인자
    "env": {  // ← 환경 변수
      "DISCORD_WEBHOOK_URL": "${DISCORD_WEBHOOK_URL}"
    }
  }
}
```

- **`discord-notifier`**: MCP 서버의 고유 이름
- **`command`**: 서버를 실행하는 명령어 (Python 인터프리터)
- **`args`**: Python 모듈을 실행하기 위한 인자
  - `-m src.discord_webhook`: `src/discord_webhook.py`를 모듈로 실행
- **`env`**: 서버에 전달할 환경 변수
  - `${DISCORD_WEBHOOK_URL}`: `.env` 파일에서 로드

#### 2. `notifications` 섹션

각 알림 타입의 활성화 여부와 설정을 정의합니다.

```json
"notifications": {
  "task_complete": {
    "enabled": true,  // ← 이 알림 타입 활성화
    "message_type": "task_complete"  // ← 메시지 타입 지정
  },
  // ... 다른 알림 타입들
}
```

---

## MCP와 일반 Python 스크립트의 차이점

### 🔴 일반 Python 스크립트

```python
# 직접 실행 방식
from src.discord_webhook import DiscordNotifier
notifier = DiscordNotifier(webhook_url)
notifier.send_notification(...)
```

**특징:**
- 사용자가 직접 Python 코드를 작성해야 함
- Claude Code와 통합되지 않음
- 수동으로 호출 시점을 관리해야 함

### 🟢 MCP 기반 시스템

```json
// MCP 설정 (discord-notify.mcp.json)
{
  "mcpServers": {
    "discord-notifier": { ... }
  }
}
```

**특징:**
- Claude Code가 자동으로 MCP 서버 호출
- `.claude/CLAUDE.md` 규칙에 따라 적절한 시점에 자동 실행
- 표준화된 프로토콜로 다른 AI 도구와도 호환 가능

---

## 이 프로젝트가 MCP를 사용하는 이유

### 1. **자동화**
- Claude Code가 작업 완료를 감지하면 자동으로 알림 전송
- 사용자가 별도로 Python 스크립트를 실행할 필요 없음

### 2. **표준화**
- MCP는 Anthropic이 제공하는 공식 프로토콜
- 다른 AI 도구에서도 동일한 설정 파일 재사용 가능

### 3. **확장성**
- 새로운 알림 타입 추가가 쉬움
- 다른 MCP 서버(Slack, Email 등)도 쉽게 통합 가능

### 4. **보안**
- 환경 변수를 통한 민감한 정보 관리
- AI가 직접 Webhook URL에 접근하지 않고 MCP 서버를 통해 간접 접근

---

## 내가 만든 것 vs Anthropic의 MCP

### ✅ 내가 만든 것

1. **`discord-notify.mcp.json`** (MCP 설정 파일)
   - MCP 서버의 실행 방법 정의
   - 알림 타입 및 활성화 설정

2. **`src/discord_webhook.py`** (MCP 서버 구현)
   - Discord Webhook API와 통신하는 로직
   - 메시지 타입별 템플릿 및 Embed 생성
   - 환경 변수 로드 및 에러 핸들링

3. **`.claude/CLAUDE.md`** (Claude Code 규칙)
   - Claude Code가 언제 MCP 서버를 호출할지 정의
   - 알림 전송 트리거 시점 및 메시지 형식 가이드라인

### 🔧 Anthropic의 MCP (Model Context Protocol)

1. **프로토콜 자체**
   - AI와 외부 도구 간의 통신 규약
   - JSON 기반 메시지 포맷
   - 서버-클라이언트 아키텍처

2. **Claude Code의 MCP 클라이언트**
   - `discord-notify.mcp.json` 파일을 파싱
   - MCP 서버 프로세스 실행 및 관리
   - AI 작업 흐름과 MCP 서버 통합

---

## MCP 서버의 역할 상세

### 1. **도구 제공자 (Tool Provider)**
MCP 서버는 Claude Code에게 "Discord 알림 전송" 도구를 제공합니다.

```python
class DiscordNotifier:
    """Discord Webhook을 통한 알림 전송 도구"""

    def send_notification(self, message_type, project_name, details, metadata):
        # Discord API로 알림 전송
        pass
```

### 2. **추상화 계층 (Abstraction Layer)**
Claude Code는 Discord Webhook API의 복잡한 세부사항을 알 필요 없이, MCP 서버를 통해 간단하게 알림을 보낼 수 있습니다.

```
Claude Code → "작업 완료 알림 보내줘" → MCP 서버 → Discord Webhook API
```

### 3. **상태 관리 (State Management)**
MCP 서버는 다음과 같은 상태를 관리합니다:
- Webhook URL (환경 변수에서 로드)
- 알림 타입별 템플릿
- 에러 핸들링 및 재시도 로직

---

## MCP가 없다면?

### 🔴 MCP 없이 직접 구현한다면:

1. **Claude Code가 Discord Webhook API를 직접 호출**
   - API 엔드포인트, 헤더, 페이로드 형식을 AI가 직접 생성해야 함
   - 에러 발생 시 처리 로직이 복잡해짐

2. **보안 문제**
   - Webhook URL을 Claude Code가 직접 알아야 함
   - 민감한 정보가 AI의 컨텍스트에 노출

3. **유지보수 어려움**
   - Discord API가 변경되면 Claude Code의 동작도 수정해야 함
   - 다른 프로젝트에 재사용하기 어려움

### 🟢 MCP를 사용하면:

1. **표준화된 인터페이스**
   - Claude Code는 "MCP 서버 호출"만 하면 됨
   - Discord API의 복잡한 세부사항은 MCP 서버가 처리

2. **보안 강화**
   - Webhook URL은 `.env` 파일에만 저장
   - MCP 서버만 민감한 정보에 접근

3. **쉬운 유지보수**
   - Discord API 변경 시 MCP 서버 코드만 수정
   - 다른 프로젝트에서도 동일한 MCP 설정 파일 재사용

---

## MCP 동작 방식 (기술적 세부사항)

### 1. Claude Code가 MCP 설정 파일 파싱

```json
// discord-notify.mcp.json
{
  "mcpServers": {
    "discord-notifier": {
      "command": "python3",
      "args": ["-m", "src.discord_webhook"]
    }
  }
}
```

Claude Code는 이 설정을 읽고 다음 명령어를 준비합니다:

```bash
python3 -m src.discord_webhook
```

### 2. MCP 서버 프로세스 실행

Claude Code가 작업 완료를 감지하면:

```bash
# 환경 변수와 함께 MCP 서버 실행
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." \
python3 -m src.discord_webhook
```

### 3. MCP 서버가 Discord에 알림 전송

```python
# src/discord_webhook.py의 main() 함수 실행
def main():
    load_dotenv()
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    notifier = DiscordNotifier(webhook_url)

    # 알림 전송
    notifier.send_notification(
        message_type="task_complete",
        project_name="프로젝트명",
        details="작업 내용",
        metadata={...}
    )
```

### 4. Claude Code가 MCP 서버 응답 처리

```
성공: ✅ Discord 알림 전송 성공
실패: ❌ Discord 알림 전송 실패 (에러 메시지)
```

---

## 이 프로젝트에서 MCP 설정 위치

### 프로젝트 구조

```
discord_mcp/
├── discord-notify.mcp.json  ← MCP 설정 파일
├── .env                      ← 환경 변수 (Webhook URL)
├── src/
│   └── discord_webhook.py   ← MCP 서버 구현
└── .claude/
    └── CLAUDE.md             ← Claude Code 규칙
```

### 각 파일의 역할

1. **`discord-notify.mcp.json`**
   - Claude Code가 읽는 MCP 서버 설정
   - 서버 실행 명령어 및 환경 변수 정의

2. **`src/discord_webhook.py`**
   - 실제 Discord 알림 전송 로직
   - MCP 서버의 "도구" 구현

3. **`.claude/CLAUDE.md`**
   - Claude Code에게 "언제" MCP 서버를 호출할지 알려줌
   - 알림 전송 트리거 시점 정의

4. **`.env`**
   - Discord Webhook URL 저장
   - MCP 서버가 런타임에 로드

---

## 내가 이 프로젝트로 한 것

### ✅ 만든 것

1. **커스텀 MCP 서버** (`discord-notifier`)
   - Discord Webhook API를 MCP 프로토콜로 래핑
   - 4가지 알림 타입 지원 (task_complete, build_complete, user_decision, error)

2. **MCP 설정 파일** (`discord-notify.mcp.json`)
   - MCP 서버의 실행 방법과 알림 설정 정의

3. **Claude Code 통합 규칙** (`.claude/CLAUDE.md`)
   - Claude Code가 작업 완료 시 자동으로 Discord 알림 전송하도록 설정

### 🔧 사용한 것

1. **Anthropic의 MCP 프로토콜**
   - AI와 외부 도구를 연결하는 표준 프로토콜
   - Claude Code의 MCP 클라이언트 기능

2. **Discord Webhook API**
   - Discord에 메시지를 전송하는 REST API

---

## 결론

### "MCP를 만들었다"는 표현의 의미

- **정확한 표현**: "MCP 프로토콜을 사용하여 Discord 알림 서버를 만들었다"
- **비유**: HTTP 프로토콜을 사용하여 웹 서버를 만든 것과 유사
  - HTTP 프로토콜 자체는 W3C가 만든 것
  - 하지만 HTTP를 사용하는 웹 서버는 개발자가 만든 것

### 이 프로젝트의 가치

1. **MCP 프로토콜 활용**: Anthropic의 표준 프로토콜을 올바르게 사용
2. **커스텀 도구 구현**: Discord 알림이라는 구체적인 기능 구현
3. **Claude Code 통합**: AI 워크플로우에 자동 알림 기능 추가
4. **재사용 가능**: 다른 프로젝트에서도 동일한 MCP 서버 사용 가능

---

## Discord Webhook 동작 원리

### Webhook이란?

**Webhook**은 역방향 API(Reverse API)라고도 불리며, 서버가 특정 이벤트 발생 시 미리 설정된 URL로 HTTP 요청을 보내는 방식입니다.

### 일반 API vs Webhook

#### 🔵 일반 API (Pull 방식)
```
클라이언트 → "데이터 주세요" → 서버
클라이언트 ← "여기 있어요" ← 서버
```
- 클라이언트가 능동적으로 서버에 요청
- 폴링(Polling): 주기적으로 데이터 확인
- 비효율적: 변경사항이 없어도 계속 요청

#### 🟢 Webhook (Push 방식)
```
서버 → "이벤트 발생했어요!" → 클라이언트
```
- 서버가 이벤트 발생 시 자동으로 클라이언트에게 알림
- 실시간: 이벤트 발생 즉시 전달
- 효율적: 필요할 때만 통신

### Discord Webhook 동작 흐름

#### 1. Webhook 생성 (일회성 설정)

```
사용자 → Discord 서버 설정 → Webhook 생성 → Webhook URL 획득
```

**Webhook URL 예시:**
```
https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz
                                    ↑                ↑
                                Webhook ID      Webhook Token
```

- **Webhook ID**: Discord가 생성한 고유 ID
- **Webhook Token**: 인증 토큰 (민감한 정보!)

#### 2. Webhook URL의 의미

```
https://discord.com/api/webhooks/[WEBHOOK_ID]/[WEBHOOK_TOKEN]
```

- Discord가 제공하는 특별한 "편지함" 주소
- 이 주소로 메시지를 보내면 Discord가 자동으로 지정된 채널에 표시
- 별도의 인증(OAuth, Bot Token) 없이도 메시지 전송 가능

#### 3. 메시지 전송 과정

```python
# 1단계: HTTP POST 요청 준비
import requests

webhook_url = "https://discord.com/api/webhooks/1234567890/abc..."
payload = {
    "embeds": [{
        "title": "작업 완료!",
        "description": "프로젝트 빌드가 완료되었습니다.",
        "color": 3066993  # 초록색
    }]
}

# 2단계: Discord Webhook API로 전송
response = requests.post(
    webhook_url,
    json=payload,
    headers={"Content-Type": "application/json"}
)

# 3단계: Discord가 채널에 메시지 표시
# → 사용자의 Discord 클라이언트에 알림 도착
```

### Webhook 통신 상세 과정

```
┌─────────────────────┐
│   Python Script     │
│ (MCP 서버)          │
└──────────┬──────────┘
           │
           │ 1. HTTP POST 요청
           │    - URL: Webhook URL
           │    - Body: JSON 페이로드
           │    - Header: Content-Type: application/json
           │
┌──────────▼──────────┐
│   Discord API       │
│   Webhook Handler   │
└──────────┬──────────┘
           │
           │ 2. Webhook 검증
           │    - Webhook ID가 유효한가?
           │    - Webhook Token이 올바른가?
           │    - 페이로드 형식이 올바른가?
           │
           │ 3. 메시지 생성
           │    - Embed 객체 파싱
           │    - 색상, 필드, 이미지 등 렌더링
           │
┌──────────▼──────────┐
│   Discord 채널       │
│   (사용자가 설정)    │
└──────────┬──────────┘
           │
           │ 4. 사용자에게 알림
           │
┌──────────▼──────────┐
│   사용자 디바이스    │
│   - 데스크톱 앱      │
│   - 모바일 앱        │
│   - 웹 브라우저      │
└─────────────────────┘
```

### Discord Webhook API 메시지 형식

#### 1. 간단한 텍스트 메시지

```json
{
  "content": "안녕하세요! 이것은 테스트 메시지입니다."
}
```

**결과:**
```
안녕하세요! 이것은 테스트 메시지입니다.
```

#### 2. Rich Embed 메시지 (이 프로젝트에서 사용)

```json
{
  "embeds": [
    {
      "title": "✅ 작업 완료!",
      "description": "🎉 **프로젝트명**",
      "color": 3066993,
      "fields": [
        {
          "name": "📅 완료 시각",
          "value": "2025-10-27 14:30:00",
          "inline": true
        },
        {
          "name": "📝 상세 내용",
          "value": "FastAPI 백엔드 구현 완료",
          "inline": false
        },
        {
          "name": "🔸 실행 시간",
          "value": "3분 45초",
          "inline": true
        }
      ],
      "footer": {
        "text": "Claude Code Notification System"
      }
    }
  ]
}
```

**결과:**
```
╔════════════════════════════════╗
║ ✅ 작업 완료!                   ║
║ 🎉 **프로젝트명**               ║
║                                ║
║ 📅 완료 시각    | 🔸 실행 시간 ║
║ 2025-10-27      | 3분 45초     ║
║ 14:30:00        |              ║
║                                ║
║ 📝 상세 내용                   ║
║ FastAPI 백엔드 구현 완료        ║
║                                ║
║ Claude Code Notification System║
╚════════════════════════════════╝
```

### 이 프로젝트에서의 Webhook 사용

#### 파일: `src/discord_webhook.py`

```python
class DiscordNotifier:
    def __init__(self, webhook_url: str):
        """Webhook URL 저장"""
        self.webhook_url = webhook_url

    def send_notification(self, message_type, project_name, details, metadata):
        # 1. Embed 메시지 구성
        embed = {
            "title": "✅ Claude Code 작업 완료!",
            "description": f"🎉 **{project_name}**",
            "color": 3066993,  # 초록색 (RGB: 46, 204, 113)
            "fields": [...]
        }

        # 2. Webhook으로 전송
        payload = {"embeds": [embed]}
        response = requests.post(
            self.webhook_url,  # Discord Webhook URL
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        # 3. 응답 확인
        if response.status_code == 204:
            # 성공: Discord가 메시지를 정상적으로 받음
            return True
        else:
            # 실패: 에러 메시지 출력
            return False
```

### Webhook URL 보안

#### ⚠️ 왜 Webhook URL을 비밀로 유지해야 하는가?

1. **공개되면 누구나 메시지 전송 가능**
   ```bash
   # 악의적인 사용자가 Webhook URL을 알게 되면:
   curl -X POST https://discord.com/api/webhooks/1234567890/abc... \
     -H "Content-Type: application/json" \
     -d '{"content": "스팸 메시지!"}'
   ```

2. **채널 스팸 공격 가능**
   - 무한 루프로 메시지 전송
   - 채널이 스팸으로 도배됨

3. **Webhook 삭제 불가능**
   - Webhook URL 자체에는 삭제 권한이 없지만
   - Discord 서버 관리자만 Webhook 삭제 가능

#### 🔒 Webhook URL 보호 방법

1. **환경 변수 사용** (이 프로젝트 방식)
   ```bash
   # .env 파일에 저장
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

   # .gitignore에 추가
   .env
   ```

2. **Git에 커밋하지 않기**
   ```gitignore
   .env
   .env.local
   *.env
   ```

3. **Webhook URL을 코드에 하드코딩하지 않기**
   ```python
   # ❌ 나쁜 예
   webhook_url = "https://discord.com/api/webhooks/1234567890/abc..."

   # ✅ 좋은 예
   webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
   ```

### Webhook 응답 코드

Discord Webhook API는 다음과 같은 HTTP 응답 코드를 반환합니다:

| 코드 | 의미 | 설명 |
|------|------|------|
| 204 No Content | ✅ 성공 | 메시지가 정상적으로 전송됨 |
| 400 Bad Request | ❌ 잘못된 요청 | JSON 형식 오류, 필수 필드 누락 |
| 401 Unauthorized | ❌ 인증 실패 | Webhook Token이 잘못됨 |
| 404 Not Found | ❌ Webhook 없음 | Webhook ID가 잘못되었거나 삭제됨 |
| 429 Too Many Requests | ⚠️ 속도 제한 | 너무 많은 요청 (1분에 30개 제한) |

### Webhook 속도 제한 (Rate Limit)

Discord는 Webhook 스팸을 방지하기 위해 속도 제한을 적용합니다:

- **제한**: 1분당 최대 30개 메시지
- **초과 시**: HTTP 429 응답 + `Retry-After` 헤더

```python
# 속도 제한 처리 예시
response = requests.post(webhook_url, json=payload)

if response.status_code == 429:
    retry_after = response.headers.get("Retry-After")
    print(f"⚠️ 속도 제한! {retry_after}초 후 재시도")
    time.sleep(int(retry_after))
    # 재시도 로직...
```

### 이 프로젝트에서의 Webhook 흐름 (종합)

```
1. 사용자가 Discord에서 Webhook 생성
   → Webhook URL 획득

2. Webhook URL을 .env 파일에 저장
   → DISCORD_WEBHOOK_URL=https://...

3. Claude Code가 작업 완료 감지
   → .claude/CLAUDE.md 규칙 참조

4. MCP 서버 실행
   → python3 -m src.discord_webhook

5. MCP 서버가 .env에서 Webhook URL 로드
   → load_dotenv()
   → webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

6. DiscordNotifier가 HTTP POST 요청 생성
   → payload = {"embeds": [...]}

7. Discord Webhook API로 전송
   → requests.post(webhook_url, json=payload)

8. Discord가 메시지 검증 및 채널에 표시
   → HTTP 204 응답

9. 사용자의 Discord 클라이언트에 알림 도착
   → 실시간 알림!
```

---

## 추가 리소스

- [Model Context Protocol 공식 문서](https://modelcontextprotocol.io/)
- [Discord Webhook API 문서](https://discord.com/developers/docs/resources/webhook)
- [Discord Embed 생성기](https://discohook.org/) - Embed 메시지 미리보기
- [Claude Code 문서](https://docs.claude.com/)

---

**작성**: Discord MCP Notifier 프로젝트
**날짜**: 2025-10-27
