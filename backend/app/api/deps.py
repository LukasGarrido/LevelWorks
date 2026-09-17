'''API dependency definitions.

This module centralises FastAPI dependencies used across the API routes.
It currently provides dependencies for obtaining an asynchronous SQLAlchemy
session and for resolving/authorizing the current authenticated user.
'''

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import the low‑level session generator defined in the core database module.
from app.core.db.database import get_db as _get_db
from app.core.jwt import decode_token
from app.models.user import User, Rol


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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """Decode the JWT, validate the user still exists, and return it.

    Raises 401 if the token is missing/invalid/expired or the user no
    longer exists in the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la credencial",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.scalars(select(User).where(User.id == int(user_id)))
    user = result.first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Restrict access to users with the ADMIN role."""
    if current_user.rol != Rol.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para esta acción",
        )
    return current_user