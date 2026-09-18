"""
app/services/catalog_service.py
Lógica de negocio para el catálogo de servicios.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.service import Service


class ServiceNotFoundError(Exception):
    """El servicio solicitado no existe."""
    pass


async def listar_servicios(db: AsyncSession, solo_activos: bool = True) -> list[Service]:
    """Obtiene el catálogo de servicios, opcionalmente filtrando solo los activos."""
    stmt = select(Service)
    if solo_activos:
        stmt = stmt.where(Service.is_active == True)
    result = await db.scalars(stmt)
    return list(result.all())


async def obtener_servicio(db: AsyncSession, service_id: int) -> Service:
    """Obtiene un servicio por id. Lanza ServiceNotFoundError si no existe."""
    result = await db.scalars(select(Service).where(Service.id == service_id))
    service = result.first()
    if not service:
        raise ServiceNotFoundError("Servicio no encontrado")
    return service


async def crear_servicio(db: AsyncSession, data: dict[str, Any]) -> Service:
    """Crea un nuevo servicio."""
    new_service = Service(**data)
    db.add(new_service)
    await db.flush()
    await db.refresh(new_service)
    return new_service


async def editar_servicio(db: AsyncSession, service_id: int, data: dict[str, Any]) -> Service:
    """Actualiza campos parciales de un servicio existente."""
    service = await obtener_servicio(db, service_id)
    for key, value in data.items():
        setattr(service, key, value)
    await db.flush()
    await db.refresh(service)
    return service


async def eliminar_servicio(db: AsyncSession, service_id: int) -> None:
    """Elimina un servicio por id."""
    service = await obtener_servicio(db, service_id)
    await db.delete(service)
    await db.flush()