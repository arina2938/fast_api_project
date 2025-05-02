"""Модуль конфигурации приложения."""

# Сторонние библиотеки
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс для хранения настроек приложения.

    Настройки загружаются из переменных окружения или файла .env.

    Attributes:
        secret_key (str): Секретный ключ для JWT (по умолчанию: "secret-key")
        algo (str): Алгоритм шифрования JWT (по умолчанию: "HS256")
        access_token_expire_minutes (int): Время жизни токена в минутах (по умолчанию: 30)
    """

    model_config = SettingsConfigDict(env_file=".env")

    secret_key: str = "secret-key"
    algo: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
