# app/api/v1/reservations.py
from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.reservation import Reservation
from app.models.client import Client, ReservationStatus
from app.models.service import Service
from app.core.db.database import async_session
from app.schemas.reservation import (
    ReservationCreateSchema,
    ReservationUpdateSchema,
    ReservationStatusUpdateSchema,
    ReservationResponseSchema,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/", response_model=List[ReservationResponseSchema])
async def get_reservations():
    """Obtiene todas las reservas."""
    async with async_session() as session:
        result = await session.scalars(select(Reservation))
        return result.all()


@router.get("/{id}", response_model=ReservationResponseSchema)
async def get_reservation(id: int):
    """Obtiene una reserva por su id."""
    async with async_session() as session:
        result = await session.scalars(select(Reservation).where(Reservation.id == id))
        reservation = result.first()
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
        return reservation


@router.post("/", response_model=ReservationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_reservation(reservation_in: ReservationCreateSchema):
    """Crea una nueva reserva."""
    async with async_session() as session:
        # Verificar que el cliente existe
        client = await session.get(Client, reservation_in.client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )

        # Verificar que el servicio existe
        service = await session.get(Service, reservation_in.service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado",
            )

        nueva_reserva = Reservation(**reservation_in.model_dump())
        session.add(nueva_reserva)

        try:
            await session.commit()
            await session.refresh(nueva_reserva)
            return nueva_reserva
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflicto: el horario seleccionado ya está ocupado",
            )


@router.put("/{id}", response_model=ReservationResponseSchema)
async def update_reservation(id: int, reservation_in: ReservationUpdateSchema):
    """Actualiza una reserva por su id."""
    async with async_session() as session:
        result = await session.scalars(select(Reservation).where(Reservation.id == id))
        reservation = result.first()
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")

        update_data = reservation_in.model_dump(exclude_unset=True)

        # Verificar FK si se cambia client_id
        if "client_id" in update_data:
            client = await session.get(Client, update_data["client_id"])
            if not client:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

        # Verificar FK si se cambia service_id
        if "service_id" in update_data:
            service = await session.get(Service, update_data["service_id"])
            if not service:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")

        for field, value in update_data.items():
            setattr(reservation, field, value)

        try:
            await session.commit()
            await session.refresh(reservation)
            return reservation
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflicto: el horario seleccionado ya está ocupado",
            )


@router.patch("/{id}/status", response_model=ReservationResponseSchema)
async def update_reservation_status(id: int, status_in: ReservationStatusUpdateSchema):
    """Actualiza únicamente el status de una reserva."""
    async with async_session() as session:
        result = await session.scalars(select(Reservation).where(Reservation.id == id))
        reservation = result.first()
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")

        reservation.status = status_in.status
        await session.commit()
        await session.refresh(reservation)
        return reservation


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(id: int):
    """Elimina una reserva por su id."""
    async with async_session() as session:
        result = await session.scalars(select(Reservation).where(Reservation.id == id))
        reservation = result.first()
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")

        await session.delete(reservation)
        await session.commit()
