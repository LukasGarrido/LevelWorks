# app/schemas/reservation.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.client import ReservationStatus


class ReservationCreateSchema(BaseModel):
    client_id: int
    service_id: int
    scheduled_at: datetime
    vehicle: str | None = None
    notes: str | None = None


class ReservationUpdateSchema(BaseModel):
    client_id: int | None = None
    service_id: int | None = None
    scheduled_at: datetime | None = None
    status: ReservationStatus | None = None
    vehicle: str | None = None
    notes: str | None = None


class ReservationStatusUpdateSchema(BaseModel):
    status: ReservationStatus


class ReservationResponseSchema(BaseModel):
    id: int
    client_id: int
    service_id: int
    scheduled_at: datetime
    status: ReservationStatus
    vehicle: str | None = None
    notes: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
