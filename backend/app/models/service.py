import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.db.database import Base
from app.core.storage import storage, ImageType

class Service(Base):
    """Servicios de lavado que ofrece el negocio."""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    photo = Column(ImageType(storage=storage), nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=30)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    reservations = relationship(
        "Reservation",
        back_populates="service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Service {self.name}>"
