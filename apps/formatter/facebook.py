from .base import BaseFormatter

class FacebookFormatter(BaseFormatter):
    def __init__(self):
        super().__init__()
        self.platform_name = "facebook"

    def format_post(self, content: str) -> str:
        # Facebook allows up to 63,206 characters
        if len(content) > 63000:
            return content[:62997] + "..."
        return content
