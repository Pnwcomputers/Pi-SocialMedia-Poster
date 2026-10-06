from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Config
    app_name: str = "Pi-SocialMedia-Poster"
    database_url: str = "sqlite:///./social_poster.db"
    
    # API Keys (Loaded from .env)
    mastodon_access_token: Optional[str] = None
    bluesky_handle: Optional[str] = None
    bluesky_password: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    linkedin_access_token: Optional[str] = None
    facebook_access_token: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
