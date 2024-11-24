"""A module providing configuration variables."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """A class containing base settings configuration."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class AppConfig(BaseConfig):
    """A class containing app's configuration."""
    DB_HOST: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    API_KEY: Optional[str] = None

config = AppConfig()