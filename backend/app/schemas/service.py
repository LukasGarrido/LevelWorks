# app/schemas/service.py
from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    duration_minutes: int = 30


class ServiceCreateSchema(ServiceBase):
    is_active: bool = True


class ServiceUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None


class ServiceResponseSchema(ServiceBase):
    id: int
    is_active: bool
    photo: str | None = None

    model_config = ConfigDict(from_attributes=True)  # permite serializar desde el ORM