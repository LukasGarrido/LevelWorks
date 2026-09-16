# app/api/v1/services.py
from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.models.service import Service
from app.core.db.database import async_session
from app.schemas.service import (
    ServiceCreateSchema,
    ServiceUpdateSchema,
    ServiceResponseSchema,
)

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/", response_model=List[ServiceResponseSchema])
async def get_services():
    """Obtiene todos los servicios activos."""
    async with async_session() as session:
        result = await session.scalars(select(Service).where(Service.is_active == True))
        return result.all()


@router.get("/{id}", response_model=ServiceResponseSchema)
async def get_service(id: int):
    """Obtiene un servicio por su id."""
    async with async_session() as session:
        result = await session.scalars(select(Service).where(Service.id == id))
        service = result.first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
        return service


@router.post("/", response_model=ServiceResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_service(service_in: ServiceCreateSchema):
    """Crea un nuevo servicio."""
    async with async_session() as session:
        nuevo_servicio = Service(**service_in.model_dump())
        session.add(nuevo_servicio)
        await session.commit()
        await session.refresh(nuevo_servicio)
        return nuevo_servicio


@router.put("/{id}", response_model=ServiceResponseSchema)
async def update_service(id: int, service_in: ServiceUpdateSchema):
    """Actualiza un servicio por su id."""
    async with async_session() as session:
        result = await session.scalars(select(Service).where(Service.id == id))
        service = result.first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")

        for field, value in service_in.model_dump(exclude_unset=True).items():
            setattr(service, field, value)

        await session.commit()
        await session.refresh(service)
        return service


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(id: int):
    """Elimina un servicio por su id."""
    async with async_session() as session:
        result = await session.scalars(select(Service).where(Service.id == id))
        service = result.first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")

        await session.delete(service)
        await session.commit()