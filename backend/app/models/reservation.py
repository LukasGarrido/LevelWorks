from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Index, text
from sqlalchemy.orm import relationship
from app.core.db.database import Base
from app.models.client import ReservationStatus


class Reservation(Base):
    """Reservas de citas de los clientes."""
    __tablename__ = "reservations"
    __table_args__ = (
        Index(
            "uq_reservation_active_slot",
            "scheduled_at",
            unique=True,
            postgresql_where=text(f"status != '{ReservationStatus.CANCELADA.value}'"),
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    status = Column(
        Enum(ReservationStatus, values_callable=lambda x: [e.value for e in x]),
        default=ReservationStatus.PENDIENTE,
        nullable=False,
    )
    vehicle = Column(String(150), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    client = relationship("Client", back_populates="reservations")
    service = relationship("Service", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation {self.id} - {self.status}>"