# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY src/ ./src/
COPY discord-notify.mcp.json .

# 환경 변수 설정 (런타임에 GCP Secret Manager에서 주입됨)
ENV DISCORD_WEBHOOK_URL=""

# 포트 노출 (Cloud Run에서 사용)
EXPOSE 8080

# 헬스체크 엔드포인트를 위한 간단한 HTTP 서버
# Cloud Run은 HTTP 엔드포인트가 필요하므로 Flask 추가
RUN pip install --no-cache-dir flask gunicorn

# Flask 앱 생성
RUN echo 'from flask import Flask, jsonify\n\
import os\n\
from src.discord_webhook import DiscordNotifier\n\
\n\
app = Flask(__name__)\n\
\n\
@app.route("/", methods=["GET"])\n\
def health_check():\n\
    return jsonify({"status": "healthy", "service": "discord-mcp-notifier"}), 200\n\
\n\
@app.route("/notify", methods=["POST"])\n\
def notify():\n\
    from flask import request\n\
    data = request.get_json()\n\
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")\n\
    if not webhook_url:\n\
        return jsonify({"error": "DISCORD_WEBHOOK_URL not configured"}), 500\n\
    \n\
    notifier = DiscordNotifier(webhook_url)\n\
    success = notifier.send_notification(\n\
        message_type=data.get("message_type", "task_complete"),\n\
        project_name=data.get("project_name", "Unknown Project"),\n\
        details=data.get("details"),\n\
        metadata=data.get("metadata")\n\
    )\n\
    \n\
    if success:\n\
        return jsonify({"status": "success"}), 200\n\
    else:\n\
        return jsonify({"status": "failed"}), 500\n\
\n\
if __name__ == "__main__":\n\
    port = int(os.environ.get("PORT", 8080))\n\
    app.run(host="0.0.0.0", port=port)' > app.py

# gunicorn으로 Flask 앱 실행
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
