"""Модуль конфигурации приложения."""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Класс для хранения настроек приложения."""

    model_config = SettingsConfigDict(env_file=".env")
    secret_key: str = "secret-key"
    algo: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./test.db"



settings = Settings()