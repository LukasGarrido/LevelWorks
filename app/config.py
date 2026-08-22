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
    CONTACT_EMAIL: str = "contacto@gmail.com"
    CONTACT_PHONE: str = "+56912345678"
    INSTAGRAM_HANDLE: str = "@xperience.cc"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class SettingsProxy:
    """Proxy dinámico para que plantillas Jinja2 y módulos lean siempre el .env actualizado."""
    def __getattr__(self, item: str):
        return getattr(get_settings(), item)


def get_settings() -> Settings:
    """Devuelve la instancia de configuración leyendo .env en tiempo real."""
    return Settings()


settings_proxy = SettingsProxy()
