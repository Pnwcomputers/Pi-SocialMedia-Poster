import httpx
from typing import List, Optional
from .base import BaseConnector
from ..schemas import PostResult
from ..config import settings
from ..formatters.linkedin import LinkedInFormatter

class LinkedInConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.platform_name = "linkedin"
        self.formatter = LinkedInFormatter()
        self.token = settings.linkedin_access_token
        self.author_urn = None

    async def authenticate(self) -> bool:
        if not self.token:
            return False
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(
                    "https://api.linkedin.com/v2/me",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                if res.status_code == 200:
                    self.author_urn = f"urn:li:person:{res.json().get('id')}"
                    return True
                return False
            except Exception:
                return False

    async def post(self, content: str, media_urls: Optional[List[str]] = None) -> PostResult:
        if not self.author_urn and not await self.authenticate():
            return PostResult(platform=self.platform_name, success=False, error_message="Auth failed")

        formatted_content = self.formatter.format_post(content)
        
        payload = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": formatted_content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    "https://api.linkedin.com/v2/ugcPosts",
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "X-Restli-Protocol-Version": "2.0.0"
                    },
                    json=payload
                )
                if res.status_code in [200, 201]:
                    return PostResult(platform=self.platform_name, success=True, post_id=res.json().get("id"))
                return PostResult(platform=self.platform_name, success=False, error_message=res.text)
            except Exception as e:
                return PostResult(platform=self.platform_name, success=False, error_message=str(e))
