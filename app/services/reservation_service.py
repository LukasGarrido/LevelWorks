from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.reservation import Reservation
from app.models.client import ReservationStatus
from typing import Any

class ReservationConflictError(Exception):
    pass

class ReservationNotFoundError(Exception):
    pass

async def crear_reserva(db: AsyncSession, data: dict[str, Any]) -> Reservation:
    new_reservation = Reservation(**data)
    db.add(new_reservation)
    try:
        await db.commit()
        await db.refresh(new_reservation)
        return new_reservation
    except IntegrityError as e:
        await db.rollback()
        raise ReservationConflictError("Reservation conflict: time slot is already taken.") from e

async def cancelar_reserva(db: AsyncSession, reservation_id: int) -> Reservation:
    stmt = select(Reservation).where(Reservation.id == reservation_id)
    result = await db.execute(stmt)
    reservation = result.scalars().first()
    
    if not reservation:
        raise ReservationNotFoundError("Reservation not found")
        
    reservation.status = ReservationStatus.CANCELADA
    await db.commit()
    await db.refresh(reservation)
    return reservation
