from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    secret_key: str = "secret-key"
    algo: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings()