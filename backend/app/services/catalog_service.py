from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.service import Service
from typing import Any

class ServiceNotFoundError(Exception):
    pass

async def listar_servicios(db: AsyncSession) -> list[Service]:
    stmt = select(Service)
    result = await db.execute(stmt)
    return result.scalars().all()

async def obtener_servicio(db: AsyncSession, service_id: int) -> Service:
    stmt = select(Service).where(Service.id == service_id)
    result = await db.execute(stmt)
    service = result.scalars().first()
    if not service:
        raise ServiceNotFoundError("Service not found")
    return service

async def crear_servicio(db: AsyncSession, data: dict[str, Any]) -> Service:
    new_service = Service(**data)
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    return new_service

async def editar_servicio(db: AsyncSession, service_id: int, data: dict[str, Any]) -> Service:
    service = await obtener_servicio(db, service_id)
    for key, value in data.items():
        if value is not None:
            setattr(service, key, value)
    await db.commit()
    await db.refresh(service)
    return service

async def eliminar_servicio(db: AsyncSession, service_id: int) -> None:
    service = await obtener_servicio(db, service_id)
    await db.delete(service)
    await db.commit()
