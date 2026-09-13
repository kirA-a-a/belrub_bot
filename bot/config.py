import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

TOKEN_ENV_CANDIDATES = (
    "TELEGRAM_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "BOT_TOKEN",
    "B0T_TOKEN",
)

TOKEN_FILE_CANDIDATES = (
    Path("/app/data/telegram_token"),
    Path("data/telegram_token"),
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    bot_token: str = Field(validation_alias="TELEGRAM_TOKEN")
    cache_ttl_seconds: int = Field(default=3600, validation_alias="CACHE_TTL_SECONDS")
    sqlite_path: Path = Field(default=Path("data/bot.db"), validation_alias="SQLITE_PATH")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")


def _clean(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1].strip()
    return value


def _find_token() -> tuple[str, str]:
    for key in TOKEN_ENV_CANDIDATES:
        raw = os.environ.get(key)
        if not raw:
            continue
        cleaned = _clean(raw)
        if cleaned:
            return f"env:{key}", cleaned

    for path in TOKEN_FILE_CANDIDATES:
        try:
            if path.is_file():
                cleaned = _clean(path.read_text(encoding="utf-8"))
                if cleaned:
                    return f"file:{path}", cleaned
        except OSError:
            continue
    return "", ""


def load_settings() -> Settings:
    source, token = _find_token()
    print(
        f"env_debug: count={len(os.environ)} "
        f"token_source={source!r} token_len={len(token)}",
        flush=True,
    )
    if not token:
        raise SystemExit(
            "No telegram token. Railway is not injecting Service Variables "
            "(only RAILWAY_* present). Fix: open each variable → enable Deploy/"
            "Runtime (not only Build), or put token in /app/data/telegram_token "
            "on a Volume, then Redeploy."
        )
    os.environ["TELEGRAM_TOKEN"] = token
    return Settings()


settings = load_settings()
