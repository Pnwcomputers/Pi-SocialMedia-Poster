from abc import ABC, abstractmethod

class BaseFormatter(ABC):
    def __init__(self):
        self.platform_name = "base"

    @abstractmethod
    def format_post(self, content: str) -> str:
        """Format and validate the post text for the specific platform's rules."""
        pass
