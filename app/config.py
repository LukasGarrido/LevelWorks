"""
app/config.py
Configuración centralizada del proyecto usando variables de entorno.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "xperience"
    DEBUG: bool = False
    PORT: int = 8000
    SECRET_KEY: str = "changeme"
    DATABASE_URL: str = "sqlite+aiosqlite:///./xperience.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Devuelve la instancia de configuración (cacheada)."""
    return Settings()
