from .base import BaseFormatter

class LinkedInFormatter(BaseFormatter):
    def __init__(self):
        super().__init__()
        self.platform_name = "linkedin"

    def format_post(self, content: str) -> str:
        # LinkedIn allows up to 3000 characters
        if len(content) > 3000:
            return content[:2997] + "..."
        return content
