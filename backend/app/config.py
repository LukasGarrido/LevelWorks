"""
app/config.py
Configuración centralizada del proyecto usando variables de entorno.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Level Works"
    DEBUG: bool = False
    PORT: int = 8000
    SECRET_KEY: str = "changeme"
    DATABASE_URL: str = "sqlite+aiosqlite:///./level_works.db"
    CORS_ORIGINS: str = "http://localhost:4323"
    CONTACT_EMAIL: str = "[EMAIL_ADDRESS]"
    CONTACT_PHONE: str = "+56912345678"
    INSTAGRAM_HANDLE: str = "@level.works.cl"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Devuelve la instancia de configuración, cacheada tras la primera lectura."""
    return Settings()


settings = get_settings()