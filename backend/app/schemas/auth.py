"""
app/schemas/auth.py
Contratos de entrada/salida para autenticación.
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str          # user id, como string (estándar JWT)
    rol: str
    exp: int          # timestamp de expiración