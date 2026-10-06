import httpx
from typing import List, Optional
from .base import BaseConnector
from ..schemas import PostResult
from ..config import settings
from ..formatters.facebook import FacebookFormatter

class FacebookConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.platform_name = "facebook"
        self.formatter = FacebookFormatter()
        self.token = settings.facebook_access_token
        # Ensure you have a Page ID in your .env if posting to a page
        self.page_id = getattr(settings, 'facebook_page_id', "me") 

    async def authenticate(self) -> bool:
        if not self.token:
            return False
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"https://graph.facebook.com/v18.0/me?access_token={self.token}")
                return res.status_code == 200
            except Exception:
                return False

    async def post(self, content: str, media_urls: Optional[List[str]] = None) -> PostResult:
        formatted_content = self.formatter.format_post(content)
        
        payload = {
            "message": formatted_content,
            "access_token": self.token
        }

        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    f"https://graph.facebook.com/v18.0/{self.page_id}/feed",
                    data=payload
                )
                if res.status_code == 200:
                    return PostResult(platform=self.platform_name, success=True, post_id=res.json().get("id"))
                return PostResult(platform=self.platform_name, success=False, error_message=res.text)
            except Exception as e:
                return PostResult(platform=self.platform_name, success=False, error_message=str(e))
