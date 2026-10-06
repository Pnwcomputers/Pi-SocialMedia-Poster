from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PostCreate(BaseModel):
    content: str
    media_urls: Optional[List[str]] = []
    platforms: List[str] # e.g., ["mastodon", "bluesky", "telegram"]
    schedule_time: Optional[datetime] = None

class PostResult(BaseModel):
    platform: str
    success: bool
    post_id: Optional[str] = None
    error_message: Optional[str] = None
