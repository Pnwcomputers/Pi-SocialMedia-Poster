from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Config
    app_name: str = "Pi-SocialMedia-Poster"
    database_url: str = "sqlite:///./social_poster.db"

    # Variables from the original .env file
    app_host: Optional[str] = None
    app_port: Optional[str] = None
    dry_run: Optional[str] = None
    mastodon_instance_url: Optional[str] = None
    linkedin_redirect_uri: Optional[str] = None
    dashboard_username: Optional[str] = None
    dashboard_password: Optional[str] = None

    # API Keys
    mastodon_access_token: Optional[str] = None
    bluesky_handle: Optional[str] = None
    bluesky_password: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    linkedin_access_token: Optional[str] = None
    facebook_access_token: Optional[str] = None

    # Pydantic v2 config: load .env and safely ignore any unexpected variables
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
