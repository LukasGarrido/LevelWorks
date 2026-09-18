# app/schemas/user.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import Rol, Permission


class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    rol: Rol = Rol.USER
    permissions: list[Permission] = [Permission.READ]


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    rol: Rol | None = None
    permissions: list[Permission] | None = None


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    rol: Rol
    permissions: list[Permission]
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)