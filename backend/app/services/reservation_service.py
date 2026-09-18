"""
app/services/reservation_service.py
Lógica de negocio para la gestión de reservas.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.reservation import Reservation
from app.models.client import Client, ReservationStatus
from app.models.service import Service
from app.services.catalog_service import ServiceNotFoundError


class ReservationConflictError(Exception):
    """El horario solicitado ya está ocupado."""
    pass


class ReservationNotFoundError(Exception):
    """La reserva solicitada no existe."""
    pass


class ClientNotFoundError(Exception):
    """El cliente solicitado no existe."""
    pass


async def obtener_o_crear_cliente(
    db: AsyncSession,
    name: str,
    email: str,
    phone: str,
) -> Client:
    """Busca un cliente por email; si no existe, lo crea."""
    result = await db.scalars(select(Client).where(Client.email == email))
    client = result.first()

    if not client:
        client = Client(name=name, email=email, phone=phone)
        db.add(client)
        await db.flush()  # asigna client.id sin cerrar la transacción

    return client


async def crear_reserva(
    db: AsyncSession,
    service_id: int,
    scheduled_at,
    client_name: str,
    client_email: str,
    client_phone: str,
    vehicle: str | None = None,
    notes: str | None = None,
) -> Reservation:
    """
    Crea una nueva reserva. Busca o crea el cliente por email
    y valida que el servicio exista antes de agendar.
    """
    service = await db.get(Service, service_id)
    if not service:
        raise ServiceNotFoundError("El servicio solicitado no existe")

    client = await obtener_o_crear_cliente(db, client_name, client_email, client_phone)

    nueva_reserva = Reservation(
        client_id=client.id,
        service_id=service_id,
        scheduled_at=scheduled_at,
        vehicle=vehicle,
        notes=notes,
    )
    db.add(nueva_reserva)

    try:
        await db.flush()
        await db.refresh(nueva_reserva)
        return nueva_reserva
    except IntegrityError as e:
        await db.rollback()
        raise ReservationConflictError("El horario seleccionado ya está ocupado") from e


async def obtener_reserva(db: AsyncSession, reservation_id: int) -> Reservation:
    """Obtiene una reserva por id. Lanza ReservationNotFoundError si no existe."""
    result = await db.scalars(select(Reservation).where(Reservation.id == reservation_id))
    reservation = result.first()
    if not reservation:
        raise ReservationNotFoundError("Reserva no encontrada")
    return reservation


async def listar_reservas(db: AsyncSession) -> list[Reservation]:
    """Obtiene todas las reservas."""
    result = await db.scalars(select(Reservation))
    return list(result.all())


async def actualizar_reserva(
    db: AsyncSession,
    reservation_id: int,
    update_data: dict[str, Any],
) -> Reservation:
    """Actualiza campos parciales de una reserva existente."""
    reservation = await obtener_reserva(db, reservation_id)

    if "service_id" in update_data:
        service = await db.get(Service, update_data["service_id"])
        if not service:
            raise ServiceNotFoundError("El servicio solicitado no existe")

    if "client_id" in update_data:
        client = await db.get(Client, update_data["client_id"])
        if not client:
            raise ClientNotFoundError("Cliente no encontrado")

    for field, value in update_data.items():
        setattr(reservation, field, value)

    try:
        await db.flush()
        await db.refresh(reservation)
        return reservation
    except IntegrityError as e:
        await db.rollback()
        raise ReservationConflictError("El horario seleccionado ya está ocupado") from e


async def actualizar_estado_reserva(
    db: AsyncSession,
    reservation_id: int,
    nuevo_estado: ReservationStatus,
) -> Reservation:
    """Actualiza únicamente el estado de una reserva."""
    reservation = await obtener_reserva(db, reservation_id)
    reservation.status = nuevo_estado
    await db.flush()
    await db.refresh(reservation)
    return reservation


async def cancelar_reserva(db: AsyncSession, reservation_id: int) -> Reservation:
    """Cancela una reserva (atajo de actualizar_estado_reserva)."""
    return await actualizar_estado_reserva(db, reservation_id, ReservationStatus.CANCELADA)


async def eliminar_reserva(db: AsyncSession, reservation_id: int) -> None:
    """Elimina una reserva por id."""
    reservation = await obtener_reserva(db, reservation_id)
    await db.delete(reservation)
    await db.flush()