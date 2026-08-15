from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select

from app.database import async_session
from app.models import User, Rol
from app.config import get_settings
from app.security import verify_password, hash_password

settings = get_settings()

class AdminAuth(AuthenticationBackend):
    def __init__(self):
        super().__init__(secret_key=settings.SECRET_KEY)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        # El formulario de SQLAdmin usa 'username' y 'password'
        # Usaremos 'username' para recibir el email
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        async with async_session() as session:
            stmt = select(User).where(User.email == username)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            # Validar que exista y sea ADMIN
            if not user or user.rol != Rol.ADMIN:
                return False

            # Validar contraseña (AQUÍ DEBERÍAS USAR UN HASH EN PRODUCCIÓN)
            if not verify_password(password, user.hashed_password):
                return False

            # Guardar el token en la sesión
            request.session.update({"token": str(user.id)})
            return True

    async def logout(self, request: Request) -> bool:
        # Limpiar la sesión al salir
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        async with async_session() as session:
            try:
                stmt = select(User).where(User.id == int(token))
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
            except ValueError:
                return False

            if not user or user.rol != Rol.ADMIN:
                return False

            return True
