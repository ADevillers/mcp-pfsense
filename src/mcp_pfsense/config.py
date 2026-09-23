"""Configuration loaded from environment / .env."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_ENV_CANDIDATES = (_PACKAGE_ROOT / ".env", Path.cwd() / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=tuple(str(p) for p in _ENV_CANDIDATES if p.is_file()) or None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    pfsense_url: str = Field(
        ...,
        description="pfSense base URL without trailing slash",
    )
    pfsense_api_key: str = Field(..., description="X-API-Key for the API user")
    pfsense_verify_tls: bool = Field(default=True)
    pfsense_timeout: float = Field(default=30.0)

    @property
    def api_base(self) -> str:
        return self.pfsense_url.rstrip("/") + "/api/v2"


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()  # type: ignore[call-arg]
    except Exception as exc:
        raise RuntimeError(
            "Missing pfSense settings. Set PFSENSE_URL and PFSENSE_API_KEY (e.g. in a .env file)."
        ) from exc


def reset_settings_cache() -> None:
    get_settings.cache_clear()
