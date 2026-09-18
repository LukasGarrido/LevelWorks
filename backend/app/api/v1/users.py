# app/api/v1/users.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_admin
from app.models.user import User
from app.schemas.user import (
    UserRegisterSchema,
    UserUpdateSchema,
    UserResponseSchema,
)
from app.services.user_service import (
    listar_usuarios,
    obtener_usuario,
    crear_usuario,
    editar_usuario,
    eliminar_usuario,
    UserNotFoundError,
    UserAlreadyExistsError,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponseSchema])
async def get_users(
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Obtiene todos los usuarios. Solo administradores."""
    return await listar_usuarios(session)


@router.get("/{id}", response_model=UserResponseSchema)
async def get_user(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Obtiene un usuario por su id. Solo administradores."""
    try:
        return await obtener_usuario(session, id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")


@router.post("/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserRegisterSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Crea un nuevo usuario interno. Solo administradores."""
    try:
        return await crear_usuario(session, user_in.model_dump())
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put("/{id}", response_model=UserResponseSchema)
async def update_user(
    id: int,
    user_in: UserUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Actualiza un usuario por su id. Solo administradores."""
    try:
        return await editar_usuario(session, id, user_in.model_dump(exclude_unset=True))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Elimina un usuario por su id. Solo administradores."""
    try:
        await eliminar_usuario(session, id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")