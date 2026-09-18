# app/api/v1/reservations.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_admin
from app.models.user import User
from app.schemas.reservation import (
    ReservationCreateSchema,
    ReservationUpdateSchema,
    ReservationStatusUpdateSchema,
    ReservationResponseSchema,
)
from app.services.reservation_service import (
    crear_reserva,
    obtener_reserva,
    listar_reservas,
    actualizar_reserva,
    actualizar_estado_reserva,
    eliminar_reserva,
    ReservationConflictError,
    ReservationNotFoundError,
    ServiceNotFoundError,
    ClientNotFoundError,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/", response_model=List[ReservationResponseSchema])
async def get_reservations(
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Obtiene todas las reservas. Solo administradores."""
    return await listar_reservas(session)


@router.get("/{id}", response_model=ReservationResponseSchema)
async def get_reservation(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Obtiene una reserva por su id. Solo administradores."""
    try:
        return await obtener_reserva(session, id)
    except ReservationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")


@router.post("/", response_model=ReservationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation_in: ReservationCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Crea una nueva reserva. Endpoint público — no requiere cuenta."""
    try:
        return await crear_reserva(
            db=session,
            service_id=reservation_in.service_id,
            scheduled_at=reservation_in.scheduled_at,
            client_name=reservation_in.client.name,
            client_email=reservation_in.client.email,
            client_phone=reservation_in.client.phone,
            vehicle=reservation_in.vehicle,
            notes=reservation_in.notes,
        )
    except ServiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    except ReservationConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto: el horario seleccionado ya está ocupado",
        )


@router.put("/{id}", response_model=ReservationResponseSchema)
async def update_reservation(
    id: int,
    reservation_in: ReservationUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Actualiza una reserva por su id. Solo administradores."""
    update_data = reservation_in.model_dump(exclude_unset=True)
    try:
        return await actualizar_reserva(session, id, update_data)
    except ReservationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    except ServiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    except ClientNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    except ReservationConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto: el horario seleccionado ya está ocupado",
        )


@router.patch("/{id}/status", response_model=ReservationResponseSchema)
async def update_reservation_status(
    id: int,
    status_in: ReservationStatusUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Actualiza únicamente el status de una reserva. Solo administradores."""
    try:
        return await actualizar_estado_reserva(session, id, status_in.status)
    except ReservationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    _admin: User = Depends(get_current_admin),
):
    """Elimina una reserva por su id. Solo administradores."""
    try:
        await eliminar_reserva(session, id)
    except ReservationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")