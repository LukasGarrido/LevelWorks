# app/api/v1/users.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_admin
from app.models.user import User
from app.core.security import hash_password
from app.schemas.user import (
    UserRegisterSchema,
    UserUpdateSchema,
    UserResponseSchema,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponseSchema])
async def get_users(
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Obtiene todos los usuarios. Solo administradores."""
    result = await session.scalars(select(User))
    return result.all()


@router.get("/{id}", response_model=UserResponseSchema)
async def get_user(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Obtiene un usuario por su id. Solo administradores."""
    result = await session.scalars(select(User).where(User.id == id))
    user = result.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.post("/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserRegisterSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Crea un nuevo usuario interno. Solo administradores."""
    existing = await session.scalars(select(User).where(User.email == user_in.email))
    if existing.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        )

    existing = await session.scalars(select(User).where(User.username == user_in.username))
    if existing.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese username",
        )

    data = user_in.model_dump()
    data["hashed_password"] = hash_password(data.pop("password"))

    nuevo_usuario = User(**data)
    session.add(nuevo_usuario)
    await session.commit()
    await session.refresh(nuevo_usuario)
    return nuevo_usuario


@router.put("/{id}", response_model=UserResponseSchema)
async def update_user(
    id: int,
    user_in: UserUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Actualiza un usuario por su id. Solo administradores."""
    result = await session.scalars(select(User).where(User.id == id))
    user = result.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data:
        if update_data["password"]:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        else:
            update_data.pop("password")

    for field, value in update_data.items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Elimina un usuario por su id. Solo administradores."""
    result = await session.scalars(select(User).where(User.id == id))
    user = result.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    await session.delete(user)
    await session.commit()