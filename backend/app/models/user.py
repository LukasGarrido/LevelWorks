import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from app.core.db.database import Base

class Permission(str, enum.Enum):
    CREATE = "crear"
    READ = "leer"
    UPDATE = "actualizar"
    DELETE = "eliminar"

class Rol(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(
        Enum(Rol, values_callable=lambda x: [e.value for e in x]),
        default=Rol.USER,
        nullable=False,
    )
    permissions = Column(JSON, default=lambda: [Permission.READ.value], nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def has_permission(self, required_permission: Permission) -> bool:
        if self.rol == Rol.ADMIN:
            return True
        return required_permission.value in self.permissions

    def __repr__(self):
        return f"<User {self.username}>"