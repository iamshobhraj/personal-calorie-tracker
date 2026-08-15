from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field, PostgresDsn, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_SETTINGS_FILE = Path(__file__).resolve()
_ENV_FILE = next(
    (parent / ".env" for parent in _SETTINGS_FILE.parents if (parent / ".env").is_file()),
    Path.cwd() / ".env",
)


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Runtime settings loaded from the environment without exposing secrets."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Personal Calorie Tracker API"
    environment: Environment = Environment.DEVELOPMENT
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    cors_origins: list[AnyHttpUrl] = Field(default_factory=list)
    database_url: PostgresDsn
    database_admin_url: PostgresDsn | None = None
    database_pool_size: int = Field(default=5, ge=1, le=10)
    database_max_overflow: int = Field(default=5, ge=0, le=10)
    jwt_secret: SecretStr
    jwt_issuer: str = "personal-calorie-tracker"
    jwt_audience: str = "personal-calorie-tracker-web"
    access_token_ttl_seconds: int = Field(default=3600, gt=0)
    refresh_token_ttl_days: int = Field(default=30, gt=0)
    refresh_cookie_secure: bool = False
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_timeout_seconds: float = Field(default=25.0, gt=0)
    upload_temp_dir: Path = Path("/tmp/calorie-tracker")
    max_image_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    max_image_pixels: int = Field(default=25_000_000, gt=0)
    max_pdf_bytes: int = Field(default=15 * 1024 * 1024, gt=0)
    max_inflight_ai_requests: int = Field(default=2, gt=0)
    ai_successes_per_user_per_day: int = Field(default=10, gt=0)

    @model_validator(mode="after")
    def validate_security_invariants(self) -> Settings:
        if not self.api_prefix.startswith("/"):
            raise ValueError("api_prefix must begin with '/'")
        if self.upload_temp_dir.resolve() == Path(self.upload_temp_dir.anchor):
            raise ValueError("upload_temp_dir must not be the filesystem root")
        if self.environment is Environment.PRODUCTION:
            secret = self.jwt_secret.get_secret_value()
            if len(secret) < 32 or secret.startswith("replace-with-"):
                raise ValueError(
                    "production JWT secret must be a non-default value of at least 32 characters"
                )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide immutable settings object."""

    return Settings()  # type: ignore[call-arg]
