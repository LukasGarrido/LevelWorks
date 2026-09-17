"""
app/api/v1/auth.py
Endpoints de autenticación.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user, create_tokens

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_async_session),
):
    """Autentica al usuario y devuelve un access token JWT."""
    user = await authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    access_token = create_tokens(user)
    return TokenResponse(access_token=access_token)