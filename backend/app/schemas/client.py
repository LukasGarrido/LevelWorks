# app/schemas/client.py
from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    name: str
    email: str
    phone: str


class ClientCreateSchema(ClientBase):
    pass


class ClientUpdateSchema(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None


class ClientResponseSchema(ClientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

