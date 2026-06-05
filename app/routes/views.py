"""
app/routes/views.py
Rutas que sirven las vistas HTML (páginas completas).
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    """Página principal – formulario de reserva de citas."""
    result = await db.execute(select(Service).order_by(Service.id))
    servicios = result.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Xperience – Reserva tu cita", "servicios": servicios},
    )
