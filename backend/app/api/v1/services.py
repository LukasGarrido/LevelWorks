# app/api/v1/services.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_admin
from app.models.user import User
from app.schemas.service import (
    ServiceCreateSchema,
    ServiceUpdateSchema,
    ServiceResponseSchema,
)
from app.services.catalog_service import (
    listar_servicios,
    obtener_servicio,
    crear_servicio,
    editar_servicio,
    eliminar_servicio,
    ServiceNotFoundError,
)

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/", response_model=List[ServiceResponseSchema])
async def get_services(session: AsyncSession = Depends(get_async_session)):
    """Obtiene todos los servicios activos. Endpoint público."""
    return await listar_servicios(session, solo_activos=True)


@router.get("/{id}", response_model=ServiceResponseSchema)
async def get_service(id: int, session: AsyncSession = Depends(get_async_session)):
    """Obtiene un servicio por su id. Endpoint público."""
    try:
        return await obtener_servicio(session, id)
    except ServiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")


@router.post("/", response_model=ServiceResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_in: ServiceCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Crea un nuevo servicio. Solo administradores."""
    return await crear_servicio(session, service_in.model_dump())


@router.put("/{id}", response_model=ServiceResponseSchema)
async def update_service(
    id: int,
    service_in: ServiceUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Actualiza un servicio por su id. Solo administradores."""
    try:
        return await editar_servicio(session, id, service_in.model_dump(exclude_unset=True))
    except ServiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Elimina un servicio por su id. Solo administradores."""
    try:
        await eliminar_servicio(session, id)
    except ServiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")