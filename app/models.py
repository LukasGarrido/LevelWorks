"""
app/models.py
Modelos relacionales del sistema de reservas para autolavado.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from fastapi_storages.integrations.sqlalchemy import FileType
from app.database import Base
from app.storage import storage


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
    rol = Column(Enum(Rol), default=Rol.USER, nullable=False)
    permissions = Column(JSON, default=lambda: [Permission.READ.value], nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def has_permission(self, required_permission: Permission) -> bool:
        if self.rol == Rol.ADMIN:
            return True
        return required_permission.value in self.permissions

    def __repr__(self):
        return f"<User {self.username}>"



class ReservationStatus(str, enum.Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"



class Client(Base):
    """Clientes registrados en el sistema."""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    reservations = relationship("Reservation", back_populates="client")

    def __repr__(self):
        return f"<Client {self.name}>"


class Service(Base):
    """Servicios de lavado que ofrece el negocio."""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    photo = Column(FileType(storage=storage), nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    reservations = relationship("Reservation", back_populates="service")

    def __repr__(self):
        return f"<Service {self.name}>"


class Reservation(Base):
    """Reservas de citas de los clientes."""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    status = Column(
        Enum(ReservationStatus),
        default=ReservationStatus.PENDIENTE,
        nullable=False,
    )
    vehicle = Column(String(150), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    client = relationship("Client", back_populates="reservations")
    service = relationship("Service", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation {self.id} - {self.status}>"
