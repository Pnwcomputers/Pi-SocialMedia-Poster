import httpx
from typing import List, Optional
from .base import BaseConnector
from ..schemas import PostResult
from ..config import settings
from ..formatters.mastodon import MastodonFormatter

class MastodonConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.platform_name = "mastodon"
        self.formatter = MastodonFormatter()
        
        # Mastodon settings fallback to mastodon.social if an instance URL isn't explicitly set
        self.instance_url = getattr(settings, 'mastodon_instance_url', "https://mastodon.social")
        self.access_token = settings.mastodon_access_token
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

    async def authenticate(self) -> bool:
        """Verify the access token with the Mastodon instance."""
        if not self.access_token:
            return False
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.instance_url}/api/v1/apps/verify_credentials", 
                    headers=self.headers
                )
                return response.status_code == 200
            except Exception:
                return False

    async def post(self, content: str, media_urls: Optional[List[str]] = None) -> PostResult:
        """Publish a status with the given parameters."""
        # Apply platform-specific formatting rules
        formatted_content = self.formatter.format_post(content)
        
        # Note: Mastodon uploading requires a two-step process.
        # First you upload the file to /api/v2/media, which returns media IDs.
        # Then you pass those media_ids to the statuses endpoint. 
        media_ids = []
        
        async with httpx.AsyncClient() as client:
            if media_urls:
                for file_path in media_urls:
                    try:
                        # Open the file in binary mode and include it in the POST request through a multipart form
                        files = {'file': open(file_path, 'rb')}
                        media_res = await client.post(
                            f"{self.instance_url}/api/v2/media",
                            headers=self.headers,
                            files=files
                        )
                        if media_res.status_code in [200, 202]:
                            media_ids.append(media_res.json().get("id"))
                    except Exception as e:
                        # Continue posting text even if a single media upload fails
                        pass

            # Step 2: Post the actual status
            payload = {"status": formatted_content}
            if media_ids:
                payload["media_ids"] = media_ids

            try:
                response = await client.post(
                    f"{self.instance_url}/api/v1/statuses", 
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return PostResult(
                        platform=self.platform_name,
                        success=True,
                        post_id=str(data.get("id"))
                    )
                else:
                    return PostResult(
                        platform=self.platform_name,
                        success=False,
                        error_message=response.text
                    )
            except Exception as e:
                return PostResult(
                    platform=self.platform_name,
                    success=False,
                    error_message=str(e)
                )
