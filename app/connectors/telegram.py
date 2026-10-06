import httpx
from typing import List, Optional
from .base import BaseConnector
from ..schemas import PostResult
from ..config import settings
from ..formatters.telegram import TelegramFormatter

class TelegramConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.platform_name = "telegram"
        self.formatter = TelegramFormatter()
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id

    async def authenticate(self) -> bool:
        # Telegram API relies solely on the bot token in the URL; getMe verifies it.
        if not self.token:
            return False
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"https://api.telegram.org/bot{self.token}/getMe")
                return res.status_code == 200
            except Exception:
                return False

    async def post(self, content: str, media_urls: Optional[List[str]] = None) -> PostResult:
        formatted_content = self.formatter.format_post(content)
        
        payload = {
            "chat_id": self.chat_id,
            "text": formatted_content
        }

        async with httpx.AsyncClient() as client:
            try:
                # Use the sendMessage endpoint via HTTP POST
                res = await client.post(
                    f"https://api.telegram.org/bot{self.token}/sendMessage",
                    json=payload
                )
                if res.status_code == 200:
                    message_id = res.json().get("result", {}).get("message_id")
                    return PostResult(platform=self.platform_name, success=True, post_id=str(message_id))
                return PostResult(platform=self.platform_name, success=False, error_message=res.text)
            except Exception as e:
                return PostResult(platform=self.platform_name, success=False, error_message=str(e))
