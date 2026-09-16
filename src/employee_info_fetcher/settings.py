from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from employee_info_fetcher.config import ENV_FILE, PROJECT_ROOT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "staging", "production"] = "development"
    app_name: str = "employee-info-fetcher"
    log_level: str = "INFO"
    log_format: Literal["text", "json"] = "text"
    redact_pii_logs: bool = False

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4o-mini"

    crew_verbose: bool = False
    service_api_key: SecretStr | None = None

    oidc_issuer: str | None = None
    oidc_audience: str | None = None

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    rate_limit: str = "60/minute"

    database_url: str | None = None
    job_worker_count: int = 2

    employee_data_file: Path = Field(
        default_factory=lambda: PROJECT_ROOT / "data" / "employees.json"
    )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def use_database(self) -> bool:
        return bool(self.database_url and self.database_url.strip())

    @model_validator(mode="after")
    def apply_production_defaults(self) -> "Settings":
        if self.is_production and not self.redact_pii_logs:
            self.redact_pii_logs = True
        return self

    def require_openai_key(self) -> str:
        if self.openai_api_key is None or not self.openai_api_key.get_secret_value().strip():
            raise ValueError(
                "OPENAI_API_KEY is not configured. Copy .env.example to .env and add your key."
            )
        return self.openai_api_key.get_secret_value()

    def require_service_api_key(self) -> str:
        if self.service_api_key is None or not self.service_api_key.get_secret_value().strip():
            raise ValueError("SERVICE_API_KEY is not configured")
        return self.service_api_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()
