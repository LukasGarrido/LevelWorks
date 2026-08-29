from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.core.security import hash_password
from typing import Any

class UserNotFoundError(Exception):
    pass

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()

async def crear_usuario(db: AsyncSession, data: dict[str, Any]) -> User:
    # Hash password if provided
    if "password" in data:
        data["hashed_password"] = hash_password(data.pop("password"))
    
    new_user = User(**data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def editar_usuario(db: AsyncSession, user_id: int, data: dict[str, Any]) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise UserNotFoundError("User not found")
        
    if "password" in data and data["password"]:
        data["hashed_password"] = hash_password(data.pop("password"))
    elif "password" in data:
        data.pop("password")
        
    for key, value in data.items():
        if value is not None:
            setattr(user, key, value)
            
    await db.commit()
    await db.refresh(user)
    return user
