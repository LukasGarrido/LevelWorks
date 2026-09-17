"""
app/services/auth_service.py
Lógica de negocio para autenticación.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import verify_password
from app.core.jwt import create_access_token


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """
    Busca al usuario por email y verifica la contraseña.
    Devuelve el User si las credenciales son válidas, None si no.
    """
    result = await db.scalars(select(User).where(User.email == email))
    user = result.first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_tokens(user: User) -> str:
    """Genera el access token para un usuario ya autenticado."""
    return create_access_token(subject=str(user.id), rol=user.rol.value)