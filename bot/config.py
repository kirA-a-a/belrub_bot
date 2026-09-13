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


def _find_token() -> str:
    # Exact and common aliases
    for key in ("BOT_TOKEN", "TELEGRAM_BOT_TOKEN", "TOKEN"):
        value = os.environ.get(key)
        if value and value.strip():
            return value.strip()

    # Case-insensitive scan (Railway/UI quirks)
    for key, value in os.environ.items():
        if key.upper() == "BOT_TOKEN" and value and value.strip():
            return value.strip()
    return ""


def load_settings() -> Settings:
    token = _find_token()
    railway_env = os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_ENVIRONMENT_NAME")
    print(
        f"env_debug: count={len(os.environ)} "
        f"has_BOT_TOKEN={'BOT_TOKEN' in os.environ} "
        f"BOT_TOKEN_len={len(os.environ.get('BOT_TOKEN', ''))} "
        f"railway_env={railway_env!r} "
        f"token_found={bool(token)}",
        flush=True,
    )
    if not token:
        raise SystemExit(
            "BOT_TOKEN empty/missing in container. "
            "Open Variables → Raw Editor, ensure line is: BOT_TOKEN=123:ABC "
            "(no quotes, no spaces). Then Deployments → Redeploy."
        )
    os.environ["BOT_TOKEN"] = token
    return Settings()


settings = load_settings()
