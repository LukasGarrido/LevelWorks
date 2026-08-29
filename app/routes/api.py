"""
app/routes/api.py
Endpoints HTMX y JSON – devuelven fragmentos HTML parciales o datos de la API.
"""

import logging
from datetime import datetime, date, time
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.config import settings_proxy
from app.core.db.database import get_db
from app.models import User, Permission, Rol, Client, Service, Reservation, ReservationStatus
from app.services.reservation_service import crear_reserva, ReservationConflictError

from app.core.security import hash_password
from app.schemas.user import UserRegisterSchema, UserUpdateSchema
from app.schemas.client import ClientSchema, ClientUpdateSchema
from app.schemas.service import ServiceSchema, ServiceUpdateSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["settings"] = settings_proxy

@router.post("/admin/crear-usuario")
async def crear_usuario(
    user_in: UserRegisterSchema,
    db: AsyncSession = Depends(get_db)
):
    try:
        nuevo_usuario = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            rol=user_in.rol,
            permissions=user_in.permissions,
        )
        db.add(nuevo_usuario)
        await db.commit()
        await db.refresh(nuevo_usuario)
        return {"mensaje": "Usuario creado correctamente"}
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        logger.exception("Error al crear usuario")
        raise HTTPException(status_code=400, detail="No se pudo crear el usuario")


@router.get("/admin/listado/usuarios")
async def obtener_listado_usuarios(
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(User).order_by(User.id)
        result = await db.execute(stmt)
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error al obtener usuarios")
        raise HTTPException(status_code=400, detail="No se pudo obtener el listado de usuarios")


@router.delete("/admin/eliminar-usuario/{id}")
async def eliminar_usuario(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(User).where(User.id == id)
        result = await db.execute(stmt)
        usuario = result.scalar_one_or_none()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        await db.delete(usuario)
        await db.commit()
        return {"mensaje": "Usuario eliminado correctamente"}
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        logger.exception("Error al eliminar usuario")
        raise HTTPException(status_code=400, detail="No se pudo eliminar el usuario")


@router.put("/admin/editar-usuario/{id}")
async def editar_usuario(
    id: int,
    user_in: UserUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(User).where(User.id == id)
        result = await db.execute(stmt)
        usuario = result.scalar_one_or_none()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Actualización parcial: solo tocar los campos que vinieron en el request
        if user_in.username is not None:
            usuario.username = user_in.username
        if user_in.email is not None:
            usuario.email = user_in.email
        if user_in.password is not None:
            usuario.hashed_password = hash_password(user_in.password)
        if user_in.rol is not None:
            usuario.rol = user_in.rol
        if user_in.permissions is not None:
            usuario.permissions = user_in.permissions

        await db.commit()
        await db.refresh(usuario)
        return {"mensaje": "Usuario editado correctamente"}
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        logger.exception("Error al editar usuario")
        raise HTTPException(status_code=400, detail="No se pudo editar el usuario")

@router.post("/admin/cargar-servicios")
async def cargar_servicios(
    servicio_in: ServiceSchema,
    db: AsyncSession = Depends(get_db)
):
    try:
        nuevo_servicio = Service(**servicio_in.model_dump())
        db.add(nuevo_servicio)
        await db.commit()
        await db.refresh(nuevo_servicio)
        return {"mensaje": "Servicio cargado correctamente"}
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        logger.exception("Error al cargar servicio")
        raise HTTPException(status_code=400, detail="No se pudo cargar el servicio")


@router.get("/admin/listado/servicios")
async def obtener_listado_servicios(
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Service).order_by(Service.id)
        result = await db.execute(stmt)
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error al obtener servicios")
        raise HTTPException(status_code=400, detail="No se pudo obtener el listado de servicios")


@router.delete("/admin/eliminar-servicios/{id}")
async def eliminar_servicio(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Service).where(Service.id == id)
        result = await db.execute(stmt)
        servicio = result.scalar_one_or_none()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        await db.delete(servicio)
        await db.commit()
        return {"mensaje": "Servicio eliminado correctamente"}
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        logger.exception("Error al eliminar servicio")
        raise HTTPException(status_code=400, detail="No se pudo eliminar el servicio")


@router.put("/admin/editar-servicios/{id}")
async def editar_servicio(
    id: int,
    servicio_in: ServiceSchema,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Service).where(Service.id == id)
        result = await db.execute(stmt)
        servicio = result.scalar_one_or_none()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        servicio.name = servicio_in.name
        servicio.description = servicio_in.description
        servicio.price = servicio_in.price
        servicio.duration_minutes = servicio_in.duration_minutes
        # nota: ServiceSchema no tiene "photo", esa línea del original
        # (servicio.photo = servicio_in.photo) se quitó porque el schema
        # no la define y hubiera lanzado AttributeError

        await db.commit()
        await db.refresh(servicio)
        return {"mensaje": "Servicio editado correctamente"}
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        logger.exception("Error al editar servicio")
        raise HTTPException(status_code=400, detail="No se pudo editar el servicio")

@router.get("/admin/listado/reservas")
async def obtener_reservas(
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Reservation).order_by(Reservation.id)
        result = await db.execute(stmt)
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error al obtener reservas")
        raise HTTPException(status_code=400, detail="No se pudo obtener el listado de reservas")


@router.get("/admin/listado/clientes")
async def obtener_clientes(
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Client).order_by(Client.id)
        result = await db.execute(stmt)
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error al obtener clientes")
        raise HTTPException(status_code=400, detail="No se pudo obtener el listado de clientes")


@router.get("/admin/listado/reservas/{id}")
async def obtener_reserva(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Reservation).where(Reservation.id == id)
        result = await db.execute(stmt)
        reserva = result.scalar_one_or_none()
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return reserva
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error al obtener reserva")
        raise HTTPException(status_code=400, detail="No se pudo obtener la reserva")

@router.get("/servicios", response_class=HTMLResponse)
async def obtener_servicios(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Service).order_by(Service.id)
        result = await db.execute(stmt)
        servicios = result.scalars().all()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"servicios": servicios},
        )
    except Exception:
        logger.exception("Error al obtener servicios para la home")
        error_html = """
        <div class="col-span-full text-center p-8 border border-neutral-800 rounded-xl bg-black">
            <p class="text-neutral-500 text-sm">Servicios no disponibles temporalmente.</p>
        </div>
        """
        return HTMLResponse(content=error_html, status_code=200)


@router.get("/horas-disponibles", response_class=HTMLResponse)
async def obtener_horas_disponibles(
    request: Request,
    fecha: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Calcula y devuelve las horas disponibles para una fecha seleccionada.
    Filtra las horas que ya están reservadas en la base de datos.
    """
    try:
        fecha_obj = date.fromisoformat(fecha)
    except ValueError:
        return HTMLResponse(
            "<div class='p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium'>Fecha inválida.</div>",
            status_code=400
        )

    inicio_dia = datetime.combine(fecha_obj, time.min)
    fin_dia = datetime.combine(fecha_obj, time.max)

    stmt = select(Reservation).where(
        Reservation.scheduled_at >= inicio_dia,
        Reservation.scheduled_at <= fin_dia,
        Reservation.status != ReservationStatus.CANCELADA
    )
    result = await db.execute(stmt)
    reservas_existentes = result.scalars().all()

    horas_ocupadas = {
        reserva.scheduled_at.strftime("%H:%M")
        for reserva in reservas_existentes
    }

    horario_total = [
        "09:00", "10:00", "11:00", "12:00", "13:00",
        "14:00", "15:00", "16:00", "17:00"
    ]

    horas_disponibles = [h for h in horario_total if h not in horas_ocupadas]

    return templates.TemplateResponse(
        request=request,
        name="components/horas_disponibles.html",
        context={
            "horas": horas_disponibles,
            "fecha": fecha
        }
    )


@router.post("/reservas", response_class=HTMLResponse)
async def crear_reserva_endpoint(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    servicio_id: int = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    notas: str | None = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Procesa el formulario de reservas, crea o recupera el cliente
    y agenda la cita en la base de datos.

    Usa la lógica compartida en app/services/reservation_service.py,
    la misma que usa la ruta de views.py — protegida contra doble
    reserva por el índice único parcial en la base de datos.
    """
    if not hora:
        return HTMLResponse(
            "<div class='p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium' role='alert'>"
            "Por favor, seleccioná una hora para tu reserva."
            "</div>",
            status_code=400
        )

    try:
        fecha_hora = datetime.fromisoformat(f"{fecha}T{hora}")
    except ValueError:
        return HTMLResponse(
            "<div class='p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium' role='alert'>"
            "Formato de fecha u hora incorrecto."
            "</div>",
            status_code=400
        )

    try:
        await crear_reserva(
            db,
            nombre=nombre,
            email=email,
            telefono=telefono,
            servicio_id=servicio_id,
            fecha_hora=fecha_hora,
            notes=notas,
        )
    except ReservationConflictError:
        return HTMLResponse(
            "<div class='p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium' role='alert'>"
            "Lo sentimos, ese horario ya ha sido reservado. Por favor elegí otro."
            "</div>"
        )

    return HTMLResponse(
        f"<div class='p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-center space-y-3'>"
        f"  <div class='flex items-center justify-center gap-2 mb-2'>"
        f"    <svg class='w-6 h-6 text-emerald-400' fill='none' stroke='currentColor' viewBox='0 0 24 24'>"
        f"      <path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M5 13l4 4L19 7'/>"
        f"    </svg>"
        f"    <h3 class='text-lg font-bold text-emerald-400'>¡Reserva agendada con éxito!</h3>"
        f"  </div>"
        f"  <p class='text-sm text-neutral-300'>"
        f"    Hola <strong class='text-white'>{nombre}</strong>, tu cita ha sido registrada para el "
        f"    <strong class='text-white'>{fecha}</strong> a las <strong class='text-white'>{hora}</strong>."
        f"  </p>"
        f"  <p class='text-xs text-neutral-500 italic mt-2'>"
        f"    Estado: Pendiente de confirmación."
        f"  </p>"
        f"</div>"
    )