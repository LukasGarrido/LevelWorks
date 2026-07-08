"""
app/routes/api.py
Endpoints HTMX – devuelven fragmentos HTML parciales.
"""

from datetime import datetime, date, time
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Client, Service, Reservation, ReservationStatus

from pydantic import BaseModel

class ServiceSchema(BaseModel):
    name: str
    description: str | None = None
    price: float
    duration_minutes: int = 30

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="app/templates")


#ENDPOINTS para parte administrativa

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
        return {"mensaje":"Servicio cargado correctamente"} 
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al cargar: {str(e)}")

@router.get("/admin/listado/servicios")
async def obtener_listado_servicios(
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt=select(Service).order_by(Service.id)
        result = await db.execute(stmt)
        servicios = result.scalars().all()
        return servicios
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener servicios: {str(e)}")

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
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al eliminar servicio: {str(e)}")

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
        servicio.photo = servicio_in.photo
        await db.commit()
        await db.refresh(servicio)
        return {"mensaje": "Servicio editado correctamente"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al editar servicio: {str(e)}")


#Endpoints para ver reservas
@router.get("/admin/listado/reservas")
async def obtener_reservas(
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Reservation).order_by(Reservation.id)
        result = await db.execute(stmt)
        reservas = result.scalars().all()
        return reservas
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener reservas: {str(e)}")

@router.get("/admin/listado/clientes")
async def obtener_clientes(
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Client).order_by(Client.id)
        result = await db.execute(stmt)
        clientes = result.scalars().all()
        return clientes
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener clientes: {str(e)}")

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
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener reserva: {str(e)}")



#------------------------------------------------------------------------------------------------------------------

#ENDPOINTS para parte web

#mostrar servicios en home princial y seleccionar servicio
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
    except Exception as e:
        error_html = """
        <div class="col-span-full text-center p-8 border border-neutral-800 rounded-xl bg-black">
            <p class="text-neutral-500 text-sm">Servicios no disponibles temporalmente.</p>
        </div>
        """
        return HTMLResponse(content=error_html, status_code=200)

        
#El usuario elige un día en la web, y nosotros le respondemos con una lista de horas libres.
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

    # 1. Definir rango del día (desde las 00:00 hasta las 23:59)
    inicio_dia = datetime.combine(fecha_obj, time.min)
    fin_dia = datetime.combine(fecha_obj, time.max)

    # 2. Consultar las reservas que ya existen para ese día y que no estén canceladas
    stmt = select(Reservation).where(
        Reservation.scheduled_at >= inicio_dia,
        Reservation.scheduled_at <= fin_dia,
        Reservation.status != ReservationStatus.CANCELADA
    )
    result = await db.execute(stmt)
    reservas_existentes = result.scalars().all()

    # 3. Mapear horas ocupadas en formato HH:MM
    horas_ocupadas = {
        reserva.scheduled_at.strftime("%H:%M")
        for reserva in reservas_existentes
    }

    # 4. Definir horario de atención del autolavado (ej: 09:00 a 17:00)
    horario_total = [
        "09:00", "10:00", "11:00", "12:00", "13:00",
        "14:00", "15:00", "16:00", "17:00"
    ]

    # 5. Filtrar las horas que no están ocupadas
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
async def crear_reserva(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    servicio_id: int = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    notas: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Procesa el formulario de reservas, crea o recupera el cliente
    y agenda la cita en la base de datos.
    """
    if not hora:
        return HTMLResponse(
            "<div class='p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium' role='alert'>"
            "Por favor, seleccioná una hora para tu reserva."
            "</div>",
            status_code=400
        )

    try:
        fecha_hora_str = f"{fecha}T{hora}"
        fecha_hora = datetime.fromisoformat(fecha_hora_str)
    except ValueError:
        return HTMLResponse(
            "<div class='p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium' role='alert'>"
            "Formato de fecha u hora incorrecto."
            "</div>",
            status_code=400
        )

    # 1. Buscar si el cliente ya existe por email
    stmt_cliente = select(Client).where(Client.email == email)
    result_cliente = await db.execute(stmt_cliente)
    cliente = result_cliente.scalar_one_or_none()

    # Si no existe, crearlo
    if not cliente:
        cliente = Client(name=nombre, email=email, phone=telefono)
        db.add(cliente)
        await db.flush()  # Obtener el ID generado antes del commit

    # 2. Verificar disponibilidad de último segundo
    stmt_dispo = select(Reservation).where(
        Reservation.scheduled_at == fecha_hora,
        Reservation.status != ReservationStatus.CANCELADA
    )
    result_dispo = await db.execute(stmt_dispo)
    conflicto = result_dispo.scalar_one_or_none()

    if conflicto:
        return HTMLResponse(
            "<div class='p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium' role='alert'>"
            "Lo sentimos, ese horario ya ha sido reservado. Por favor elegí otro."
            "</div>"
        )

    # 3. Crear la reserva
    nueva_reserva = Reservation(
        client_id=cliente.id,
        service_id=servicio_id,
        scheduled_at=fecha_hora,
        status=ReservationStatus.PENDIENTE,
        notes=notas
    )
    db.add(nueva_reserva)
    await db.commit()

    # Retornar mensaje de éxito estilizado en dark theme
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
