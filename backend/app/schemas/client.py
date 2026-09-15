from pydantic import BaseModel


class ClientSchema(BaseModel):
    name: str
    email: str
    phone: str


class ClientUpdateSchema(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
