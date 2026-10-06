from abc import ABC, abstractmethod
from typing import List, Optional
from ..schemas import PostResult

class BaseConnector(ABC):
    def __init__(self):
        self.platform_name = "base"

    @abstractmethod
    async def authenticate(self) -> bool:
        """Verify credentials with the platform."""
        pass

    @abstractmethod
    async def post(self, content: str, media_urls: Optional[List[str]] = None) -> PostResult:
        """Publish content to the platform."""
        pass
