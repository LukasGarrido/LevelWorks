"""
create_admin.py
Script para crear (o actualizar) un usuario administrador.
Uso: python create_admin.py
"""
import asyncio
from getpass import getpass

from sqlalchemy import select

from app.database import async_session
from app.models import User, Rol
from app.security import hash_password


async def create_admin():
    email = input("Email del admin: ").strip()
    username = input("Username: ").strip()
    password = getpass("Password: ").strip()
    password_confirm = getpass("Confirmar password: ").strip()

    if password != password_confirm:
        print("Las contraseñas no coinciden.")
        return

    async with async_session() as session:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            existing_user.hashed_password = hash_password(password)
            existing_user.rol = Rol.ADMIN
            existing_user.username = username
            await session.commit()
            print(f"Usuario '{email}' actualizado a ADMIN con nueva contraseña.")
        else:
            new_user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                rol=Rol.ADMIN,
            )
            session.add(new_user)
            await session.commit()
            print(f"Usuario admin '{email}' creado correctamente.")


if __name__ == "__main__":
    asyncio.run(create_admin())