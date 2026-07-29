from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPSPILOT_", env_file=".env", extra="ignore")

    env: str = "development"
    database_url: str = "sqlite:///./opspilot.db"
    dev_token_secret: SecretStr
    dev_token_ttl_seconds: int = Field(default=3600, ge=1)

    @field_validator("dev_token_secret")
    @classmethod
    def require_private_signing_key(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().strip()) < 32:
            raise ValueError("OPSPILOT_DEV_TOKEN_SECRET must contain at least 32 characters")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
