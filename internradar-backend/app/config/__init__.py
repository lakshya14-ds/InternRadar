"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the InternRadar backend."""

    mongo_uri: str = Field(..., alias="MONGO_URI")
    db_name: str = Field("internradar", alias="DB_NAME")
    bot_token: str | None = Field(None, alias="BOT_TOKEN")
    chat_id: str | None = Field(None, alias="CHAT_ID")
    scraper_interval_minutes: int = Field(30, alias="SCRAPER_INTERVAL_MINUTES")
    smtp_host: str | None = Field(None, alias="SMTP_HOST")
    smtp_port: int = Field(587, alias="SMTP_PORT")
    smtp_username: str | None = Field(None, alias="SMTP_USERNAME")
    smtp_password: str | None = Field(None, alias="SMTP_PASSWORD")
    email_from: str | None = Field(None, alias="EMAIL_FROM")
    email_to: str | None = Field(None, alias="EMAIL_TO")
    discord_webhook_url: str | None = Field(None, alias="DISCORD_WEBHOOK_URL")
    twilio_account_sid: str | None = Field(None, alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = Field(None, alias="TWILIO_AUTH_TOKEN")
    twilio_whatsapp_from: str | None = Field(None, alias="TWILIO_WHATSAPP_FROM")
    twilio_whatsapp_to: str | None = Field(None, alias="TWILIO_WHATSAPP_TO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
