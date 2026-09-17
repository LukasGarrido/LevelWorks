# app/api/v1/clients.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_admin
from app.models.client import Client
from app.models.user import User
from app.schemas.client import (
    ClientCreateSchema,
    ClientUpdateSchema,
    ClientResponseSchema,
)

router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
)


@router.get("/", response_model=List[ClientResponseSchema])
async def get_clients(
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Obtiene todos los clientes. Solo administradores."""
    result = await session.scalars(select(Client))
    return result.all()


@router.get("/{id}", response_model=ClientResponseSchema)
async def get_client(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Obtiene un cliente por su id. Solo administradores."""
    result = await session.scalars(select(Client).where(Client.id == id))
    client = result.first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return client


@router.post("/", response_model=ClientResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_in: ClientCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Crea un nuevo cliente manualmente. Solo administradores.

    El alta automática de clientes durante el flujo de reservas se
    maneja internamente en reservation_service, no a través de este
    endpoint.
    """
    nuevo_cliente = Client(**client_in.model_dump())
    session.add(nuevo_cliente)
    await session.commit()
    await session.refresh(nuevo_cliente)
    return nuevo_cliente


@router.put("/{id}", response_model=ClientResponseSchema)
async def update_client(
    id: int,
    client_in: ClientUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Actualiza un cliente por su id. Solo administradores."""
    result = await session.scalars(select(Client).where(Client.id == id))
    client = result.first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    for field, value in client_in.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    await session.commit()
    await session.refresh(client)
    return client


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Elimina un cliente por su id. Solo administradores."""
    result = await session.scalars(select(Client).where(Client.id == id))
    client = result.first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    await session.delete(client)
    await session.commit()