'''API dependency definitions.

This module centralises FastAPI dependencies used across the API routes.
It currently provides a dependency for obtaining an asynchronous SQLAlchemy
session. Additional dependencies (e.g., authentication, permission checks)
can be added here as the project grows.
'''

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Import the low‑level session generator defined in the core database module.
from app.core.db.database import get_db as _get_db


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async SQLAlchemy session.

    The underlying ``_get_db`` generator handles session lifecycle – it
    commits on success, rolls back on exception and always closes the session.
    ``Depends`` can be used directly with this function in route handlers.
    """
    async for session in _get_db():
        yield session


# Alias that can be imported by route modules for brevity.
# ``Depends(get_async_session)`` will provide a ready‑to‑use ``AsyncSession``.
async_session_dependency = Depends(get_async_session)
