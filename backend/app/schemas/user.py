from pydantic import BaseModel
from app.models.user import Rol, Permission
class UserRegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    rol: Rol
    permissions: list[Permission]


class UserLoginSchema(BaseModel):
    email: str
    password: str


class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    rol: Rol | None = None
    permissions: list[Permission] | None = None
