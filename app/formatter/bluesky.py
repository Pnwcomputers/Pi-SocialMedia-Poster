from .base import BaseFormatter

class BlueskyFormatter(BaseFormatter):
    def __init__(self):
        super().__init__()
        self.platform_name = "bluesky"

    def format_post(self, content: str) -> str:
        # Bluesky has a strict 300 character limit
        if len(content) > 300:
            return content[:297] + "..."
        return content
