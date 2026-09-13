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


def _clean(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1].strip()
    return value


def _find_token() -> str:
    # BOT_TOKEN + common typo B0T_TOKEN (zero instead of O)
    for key in ("BOT_TOKEN", "B0T_TOKEN", "TELEGRAM_BOT_TOKEN", "TOKEN"):
        value = os.environ.get(key)
        if value:
            cleaned = _clean(value)
            if cleaned:
                return cleaned

    for key, value in os.environ.items():
        normalized = key.upper().replace("0", "O")
        if normalized == "BOT_TOKEN" and value:
            cleaned = _clean(value)
            if cleaned:
                return cleaned
    return ""


def load_settings() -> Settings:
    token = _find_token()
    print(
        f"env_debug: count={len(os.environ)} "
        f"keys_tokenish={[k for k in os.environ if 'TOKEN' in k.upper()]} "
        f"token_found={bool(token)} token_len={len(token)}",
        flush=True,
    )
    if not token:
        raise SystemExit(
            "BOT_TOKEN empty/missing. Raw Editor must have exactly: "
            "BOT_TOKEN=123456:ABC  (letter O in BOT, no quotes). Then Redeploy."
        )
    os.environ["BOT_TOKEN"] = token
    return Settings()


settings = load_settings()
