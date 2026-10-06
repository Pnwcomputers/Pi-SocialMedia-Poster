from .base import BaseFormatter

class TelegramFormatter(BaseFormatter):
    def __init__(self):
        super().__init__()
        self.platform_name = "telegram"

    def format_post(self, content: str) -> str:
        # Telegram allows up to 4096 characters per message
        if len(content) > 4096:
            return content[:4093] + "..."
        return content
