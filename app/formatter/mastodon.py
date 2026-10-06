from .base import BaseFormatter

class MastodonFormatter(BaseFormatter):
    def __init__(self):
        super().__init__()
        self.platform_name = "mastodon"

    def format_post(self, content: str) -> str:
        # Truncate content to Mastodon's 500 character limit if necessary
        if len(content) > 500:
            return content[:497] + "..."
        return content
