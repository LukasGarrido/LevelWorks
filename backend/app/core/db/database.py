"""
app/database.py
Configuración de la conexión asíncrona a la base de datos con SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos."""
    pass


async def get_db() -> AsyncSession:
    """Dependencia de FastAPI que provee una sesión de base de datos."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Crea todas las tablas definidas en los modelos."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
