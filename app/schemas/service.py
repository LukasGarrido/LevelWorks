from pydantic import BaseModel

class ServiceSchema(BaseModel):
    name: str
    description: str
    price: float
    image: str


class ServiceUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    image: str | None = None