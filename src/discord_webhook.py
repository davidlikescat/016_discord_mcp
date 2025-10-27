"""
Discord Webhook 핸들러
Claude Code 작업 완료 시 Discord로 알림 전송
"""

import requests
import json
from datetime import datetime
from typing import Optional, Dict


class DiscordNotifier:
    """Discord Webhook을 통한 알림 전송 클래스"""

    def __init__(self, webhook_url: str):
        """
        Args:
            webhook_url (str): Discord Webhook URL
        """
        self.webhook_url = webhook_url

    def send_notification(
        self,
        message_type: str,
        project_name: str = "Claude Code Project",
        details: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Discord로 알림 전송

        Args:
            message_type (str): 'task_complete', 'build_complete', 'user_decision'
            project_name (str): 프로젝트 이름
            details (str): 추가 상세 정보
            metadata (Dict): 메타데이터 (실행시간, 에러 등)

        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 메시지 타입별 템플릿
            templates = {
                "task_complete": {
                    "title": "✅ Claude Code 작업 완료!",
                    "color": 3066993,  # Green
                    "emoji": "🎉"
                },
                "build_complete": {
                    "title": "🏗️ 빌드 완료!",
                    "color": 3447003,  # Blue
                    "emoji": "🚀"
                },
                "user_decision": {
                    "title": "❓ 사용자 의사결정 필요",
                    "color": 15844367,  # Yellow/Orange
                    "emoji": "⚠️"
                },
                "error": {
                    "title": "❌ 오류 발생",
                    "color": 15158332,  # Red
                    "emoji": "🚨"
                }
            }

            template = templates.get(message_type, templates["task_complete"])
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Discord Embed 형식으로 메시지 구성
            embed = {
                "title": template["title"],
                "description": f"{template['emoji']} **{project_name}**",
                "color": template["color"],
                "fields": [
                    {
                        "name": "📅 완료 시각",
                        "value": current_time,
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Claude Code Notification System"
                }
            }

            # 추가 상세 정보
            if details:
                embed["fields"].append({
                    "name": "📝 상세 내용",
                    "value": details,
                    "inline": False
                })

            # 메타데이터 추가
            if metadata:
                for key, value in metadata.items():
                    embed["fields"].append({
                        "name": f"🔸 {key}",
                        "value": str(value),
                        "inline": True
                    })

            # Webhook payload
            payload = {
                "embeds": [embed]
            }

            # Discord로 전송
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 204:
                print(f"✅ Discord 알림 전송 성공: {message_type}")
                return True
            else:
                print(f"❌ Discord 알림 전송 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Discord 알림 전송 오류: {e}")
            return False

    def send_simple_message(self, content: str) -> bool:
        """
        간단한 텍스트 메시지 전송

        Args:
            content (str): 전송할 메시지

        Returns:
            bool: 전송 성공 여부
        """
        try:
            payload = {"content": content}
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            return response.status_code == 204

        except Exception as e:
            print(f"❌ 메시지 전송 오류: {e}")
            return False


def main():
    """테스트용 메인 함수"""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        return

    notifier = DiscordNotifier(webhook_url)

    # 테스트 1: 작업 완료 알림
    print("\n📤 테스트 1: 작업 완료 알림")
    notifier.send_notification(
        message_type="task_complete",
        project_name="001_discord_to_notion",
        details="YouTube to Notion 봇 구현 완료",
        metadata={
            "실행 시간": "2분 34초",
            "처리된 파일": "12개"
        }
    )

    # 테스트 2: 빌드 완료 알림
    print("\n📤 테스트 2: 빌드 완료 알림")
    notifier.send_notification(
        message_type="build_complete",
        project_name="FastAPI Backend",
        details="Production 빌드 완료",
        metadata={
            "빌드 타입": "Production",
            "번들 크기": "2.3MB"
        }
    )

    # 테스트 3: 사용자 의사결정 필요
    print("\n📤 테스트 3: 사용자 의사결정 필요")
    notifier.send_notification(
        message_type="user_decision",
        project_name="Database Migration",
        details="데이터베이스 마이그레이션을 실행하시겠습니까?\n\n• 영향받는 테이블: users, posts, comments\n• 예상 소요 시간: 5-10분",
        metadata={
            "마이그레이션 파일": "20251027_add_user_profile.sql",
            "위험도": "중간"
        }
    )

    # 테스트 4: 간단한 메시지
    print("\n📤 테스트 4: 간단한 메시지")
    notifier.send_simple_message("🎉 Claude Code 테스트 메시지입니다!")

    print("\n✅ 모든 테스트 완료!")


if __name__ == "__main__":
    main()
