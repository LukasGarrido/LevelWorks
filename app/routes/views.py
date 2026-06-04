"""
app/routes/views.py
Rutas que sirven las vistas HTML (páginas completas).
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal – formulario de reserva de citas."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Xperience – Reserva tu cita"},
    )
