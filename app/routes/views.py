"""
app/routes/views.py
Rutas que sirven las vistas HTML completas y fragmentos HTMX del asistente.
"""

import calendar
from datetime import date, datetime, time
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings_proxy
from app.database import get_db
from app.models import Service, Reservation, Client, ReservationStatus

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["settings"] = settings_proxy

# Configuración del calendario en español
SPANISH_MONTHS = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
SPANISH_WEEKDAYS = {
    0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"
}

def format_spanish_date(date_obj: date) -> str:
    weekday = SPANISH_WEEKDAYS[date_obj.weekday()]
    day = date_obj.day
    month = SPANISH_MONTHS[date_obj.month].lower()
    return f"{weekday}, {day} de {month}"

def get_calendar_weeks(year: int, month: int):
    """Genera las semanas y días del mes para el calendario de Jinja2."""
    cal = calendar.Calendar(firstweekday=6)  # Empieza en Domingo (Su Mo Tu We Th Fr Sa)
    weeks = []
    today = date.today()
    
    for week in cal.monthdayscalendar(year, month):
        week_days = []
        for day in week:
            if day == 0:
                week_days.append({
                    "day": "",
                    "date_str": "",
                    "is_today": False,
                    "is_past": True,
                    "is_sunday": False,
                    "selectable": False
                })
            else:
                day_date = date(year, month, day)
                is_today = day_date == today
                is_past = day_date < today
                is_sunday = day_date.weekday() == 6
                # El negocio atiende de Lun a Sáb, por lo que Domingo no es seleccionable
                selectable = not is_past and not is_sunday
                week_days.append({
                    "day": day,
                    "date_str": day_date.isoformat(),
                    "is_today": is_today,
                    "is_past": is_past,
                    "is_sunday": is_sunday,
                    "selectable": selectable
                })
        weeks.append(week_days)
    return weeks


# RUTA 1: HOME
@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    """Página principal – Rediseñada a fondo blanco minimalista."""
    result = await db.execute(select(Service).order_by(Service.id))
    servicios = result.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"request": request, "title": "Xperience – Detailing Profesional", "servicios": servicios},
    )


# RUTA 2: SERVICIOS (CATÁLOGO)
@router.get("/servicios", response_class=HTMLResponse)
async def servicios(request: Request, db: AsyncSession = Depends(get_db)):
    """Página de catálogo completo de servicios."""
    result = await db.execute(select(Service).order_by(Service.id))
    servicios = result.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="servicios.html",
        context={"request": request, "title": "Nuestros Servicios — Xperience", "servicios": servicios},
    )


# RUTA 3: RESERVAS (CONTENEDOR WIZARD MULTIPASO)
@router.get("/reservas", response_class=HTMLResponse)
async def reservas(
    request: Request,
    servicio_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Página contenedora del asistente de reserva."""
    result = await db.execute(select(Service).order_by(Service.id))
    servicios = result.scalars().all()
    
    # Si viene con servicio_id, cargamos directamente el paso 2
    initial_step = 2 if servicio_id else 1
    
    return templates.TemplateResponse(
        request=request,
        name="reservas.html",
        context={
            "request": request,
            "title": "Reservar Cita — Xperience",
            "servicios": servicios,
            "selected_servicio_id": servicio_id,
            "initial_step": initial_step
        },
    )


# ==========================================
# ENDPOINTS FRAGMENTOS HTMX DEL ASISTENTE
# ==========================================

@router.get("/reservas/paso1", response_class=HTMLResponse)
async def paso1(request: Request, db: AsyncSession = Depends(get_db)):
    """Paso 1: Selección de Servicio (HTMX fragment)."""
    result = await db.execute(select(Service).order_by(Service.id))
    servicios = result.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="reservas/step1_services.html",
        context={"request": request, "servicios": servicios}
    )


@router.get("/reservas/paso2", response_class=HTMLResponse)
async def paso2(
    request: Request,
    servicio_id: int = Query(...),
    year: int | None = Query(None),
    month: int | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Paso 2: Selección de Fecha y Hora (HTMX fragment)."""
    today = date.today()
    if year is None or month is None:
        year = today.year
        month = today.month
        
    # Obtener info del servicio seleccionado para la barra inferior
    result = await db.execute(select(Service).where(Service.id == servicio_id))
    servicio = result.scalar_one_or_none()
    
    calendar_weeks = get_calendar_weeks(year, month)
    month_name = SPANISH_MONTHS[month]
    
    # Calcular mes anterior/siguiente para navegación
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    # No permitir ir a meses anteriores al actual
    is_prev_disabled = (prev_year < today.year) or (prev_year == today.year and prev_month < today.month)
    
    return templates.TemplateResponse(
        request=request,
        name="reservas/step2_datetime.html",
        context={
            "request": request,
            "servicio_id": servicio_id,
            "servicio": servicio,
            "calendar_weeks": calendar_weeks,
            "year": year,
            "month": month,
            "month_name": month_name,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
            "is_prev_disabled": is_prev_disabled
        }
    )


@router.get("/reservas/horas", response_class=HTMLResponse)
async def reservas_horas(
    request: Request,
    servicio_id: int = Query(...),
    fecha: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Carga los slots de hora para la fecha seleccionada y atenúa las ya reservadas."""
    try:
        fecha_obj = date.fromisoformat(fecha)
    except ValueError:
        return HTMLResponse("<p class='text-red-500 text-xs'>Fecha inválida</p>")
        
    # Definir rango del día
    inicio_dia = datetime.combine(fecha_obj, time.min)
    fin_dia = datetime.combine(fecha_obj, time.max)
    
    # Consultar reservas ocupadas
    stmt = select(Reservation).where(
        Reservation.scheduled_at >= inicio_dia,
        Reservation.scheduled_at <= fin_dia,
        Reservation.status != ReservationStatus.CANCELADA
    )
    result = await db.execute(stmt)
    reservas_existentes = result.scalars().all()
    
    horas_ocupadas = {
        reserva.scheduled_at.strftime("%H:%M") for reserva in reservas_existentes
    }
    
    # Lista de slots de atención según el diseño
    horario_total = [
        "09:00", "09:45", "10:30", "11:15", "12:00", 
        "14:00", "14:45", "15:30", "16:15", "17:00", "17:45"
    ]
    
    slots = []
    for h in horario_total:
        slots.append({
            "hora": h,
            "is_occupied": h in horas_ocupadas
        })
        
    fecha_formateada = format_spanish_date(fecha_obj)
    
    return templates.TemplateResponse(
        request=request,
        name="reservas/horas_disponibles_reserva.html",
        context={
            "request": request,
            "slots": slots,
            "fecha": fecha,
            "fecha_formateada": fecha_formateada
        }
    )


@router.post("/reservas/paso3", response_class=HTMLResponse)
async def paso3(
    request: Request,
    servicio_id: int = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Paso 3: Formulario de datos personales (HTMX fragment)."""
    result = await db.execute(select(Service).where(Service.id == servicio_id))
    servicio = result.scalar_one_or_none()
    
    fecha_obj = date.fromisoformat(fecha)
    fecha_formateada = format_spanish_date(fecha_obj)
    
    return templates.TemplateResponse(
        request=request,
        name="reservas/step3_details.html",
        context={
            "request": request,
            "servicio_id": servicio_id,
            "servicio": servicio,
            "fecha": fecha,
            "fecha_formateada": fecha_formateada,
            "hora": hora
        }
    )


@router.post("/reservas/confirmar", response_class=HTMLResponse)
async def confirmar_reserva(
    request: Request,
    servicio_id: int = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    nombre: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    vehiculo: str = Form(...),
    notes: str = Form(None),  # Map directly to SQLAlchemy notes field
    db: AsyncSession = Depends(get_db)
):
    """Paso 4: Crea la reserva y retorna el fragmento de recibo final de éxito (HTMX)."""
    try:
        fecha_hora_str = f"{fecha}T{hora}"
        fecha_hora = datetime.fromisoformat(fecha_hora_str)
    except ValueError:
        return HTMLResponse(
            "<div class='p-4 rounded-xl bg-red-100 border border-red-200 text-red-700 text-sm'>Formato de fecha u hora incorrecto.</div>"
        )
        
    # 1. Buscar o crear cliente
    stmt_cliente = select(Client).where(Client.email == email)
    result_cliente = await db.execute(stmt_cliente)
    cliente = result_cliente.scalar_one_or_none()
    
    if not cliente:
        cliente = Client(name=nombre, email=email, phone=telefono)
        db.add(cliente)
        await db.flush()  # Generar ID antes del commit
        
    # 2. Verificar disponibilidad de último segundo
    stmt_dispo = select(Reservation).where(
        Reservation.scheduled_at == fecha_hora,
        Reservation.status != ReservationStatus.CANCELADA
    )
    result_dispo = await db.execute(stmt_dispo)
    conflicto = result_dispo.scalar_one_or_none()
    
    if conflicto:
        return HTMLResponse(
            "<div class='p-4 rounded-xl bg-red-100 border border-red-200 text-red-700 text-sm'>El horario seleccionado ya ha sido reservado. Por favor, regresa y escoge otro.</div>"
        )
        
    # 3. Crear reserva
    nueva_reserva = Reservation(
        client_id=cliente.id,
        service_id=servicio_id,
        scheduled_at=fecha_hora,
        status=ReservationStatus.PENDIENTE,
        vehicle=vehiculo,
        notes=notes
    )
    db.add(nueva_reserva)
    await db.commit()
    await db.refresh(nueva_reserva)
    
    # 4. Obtener información del servicio para el recibo
    result_service = await db.execute(select(Service).where(Service.id == servicio_id))
    servicio = result_service.scalar_one_or_none()
    
    fecha_obj = date.fromisoformat(fecha)
    fecha_formateada = format_spanish_date(fecha_obj)
    
    return templates.TemplateResponse(
        request=request,
        name="reservas/step4_receipt.html",
        context={
            "request": request,
            "reserva_id": nueva_reserva.id,
            "servicio": servicio,
            "fecha_formateada": fecha_formateada,
            "hora": hora,
            "email": email
        }
    )
