import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    bot_token: str = Field(validation_alias="BOT_TOKEN")
    cache_ttl_seconds: int = Field(default=3600, validation_alias="CACHE_TTL_SECONDS")
    sqlite_path: Path = Field(default=Path("data/bot.db"), validation_alias="SQLITE_PATH")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")


def load_settings() -> Settings:
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "BOT_TOKEN missing. In Railway: belrub_bot → Variables → "
            "add BOT_TOKEN → click Save (checkmark) → Redeploy."
        )
    # Ensure pydantic sees it even if alias quirks appear
    os.environ["BOT_TOKEN"] = token
    return Settings()


settings = load_settings()
