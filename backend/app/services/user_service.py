"""
app/services/user_service.py
Lógica de negocio para la gestión de usuarios internos.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import hash_password


class UserNotFoundError(Exception):
    """El usuario solicitado no existe."""
    pass


class UserAlreadyExistsError(Exception):
    """Ya existe un usuario con ese email o username."""
    pass


async def listar_usuarios(db: AsyncSession) -> list[User]:
    """Obtiene todos los usuarios."""
    result = await db.scalars(select(User))
    return list(result.all())


async def obtener_usuario(db: AsyncSession, user_id: int) -> User:
    """Obtiene un usuario por id. Lanza UserNotFoundError si no existe."""
    result = await db.scalars(select(User).where(User.id == user_id))
    user = result.first()
    if not user:
        raise UserNotFoundError("Usuario no encontrado")
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Busca un usuario por email. Devuelve None si no existe (uso interno, ej. login)."""
    result = await db.scalars(select(User).where(User.email == email))
    return result.first()


async def crear_usuario(db: AsyncSession, data: dict[str, Any]) -> User:
    """Crea un nuevo usuario, validando email/username duplicados y hasheando la password."""
    existing = await db.scalars(select(User).where(User.email == data["email"]))
    if existing.first():
        raise UserAlreadyExistsError("Ya existe un usuario con ese email")

    existing = await db.scalars(select(User).where(User.username == data["username"]))
    if existing.first():
        raise UserAlreadyExistsError("Ya existe un usuario con ese username")

    data["hashed_password"] = hash_password(data.pop("password"))

    new_user = User(**data)
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    return new_user


async def editar_usuario(db: AsyncSession, user_id: int, data: dict[str, Any]) -> User:
    """Actualiza campos parciales de un usuario existente."""
    user = await obtener_usuario(db, user_id)

    if "password" in data:
        if data["password"]:
            data["hashed_password"] = hash_password(data.pop("password"))
        else:
            data.pop("password")

    for key, value in data.items():
        setattr(user, key, value)

    await db.flush()
    await db.refresh(user)
    return user


async def eliminar_usuario(db: AsyncSession, user_id: int) -> None:
    """Elimina un usuario por id."""
    user = await obtener_usuario(db, user_id)
    await db.delete(user)
    await db.flush()