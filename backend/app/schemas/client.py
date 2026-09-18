# app/schemas/client.py
from pydantic import BaseModel, EmailStr, ConfigDict


class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str


class ClientCreateSchema(ClientBase):
    pass


class ClientUpdateSchema(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class ClientResponseSchema(ClientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)