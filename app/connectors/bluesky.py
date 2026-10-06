import httpx
from datetime import datetime, timezone
from typing import List, Optional
from .base import BaseConnector
from ..schemas import PostResult
from ..config import settings
from ..formatters.bluesky import BlueskyFormatter

class BlueskyConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.platform_name = "bluesky"
        self.formatter = BlueskyFormatter()
        self.handle = settings.bluesky_handle
        self.password = settings.bluesky_password
        self.base_url = "https://bsky.social/xrpc"
        self.token = None
        self.did = None

    async def authenticate(self) -> bool:
        if not self.handle or not self.password:
            return False
        
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    f"{self.base_url}/com.atproto.server.createSession",
                    json={"identifier": self.handle, "password": self.password}
                )
                if res.status_code == 200:
                    data = res.json()
                    self.token = data.get("accessJwt")
                    self.did = data.get("did")
                    return True
                return False
            except Exception:
                return False

    async def post(self, content: str, media_urls: Optional[List[str]] = None) -> PostResult:
        if not self.token and not await self.authenticate():
            return PostResult(platform=self.platform_name, success=False, error_message="Auth failed")

        formatted_content = self.formatter.format_post(content)
        
        # Note: Bluesky media uploads require a separate blob upload endpoint first.
        # This implementation covers standard text records.
        payload = {
            "repo": self.did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": formatted_content,
                "createdAt": datetime.now(timezone.utc).isoformat()
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    f"{self.base_url}/com.atproto.repo.createRecord",
                    headers={"Authorization": f"Bearer {self.token}"},
                    json=payload
                )
                if res.status_code == 200:
                    return PostResult(platform=self.platform_name, success=True, post_id=res.json().get("uri"))
                return PostResult(platform=self.platform_name, success=False, error_message=res.text)
            except Exception as e:
                return PostResult(platform=self.platform_name, success=False, error_message=str(e))
