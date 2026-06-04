"""
app/routes/api.py
Endpoints HTMX – devuelven fragmentos HTML parciales.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------------------------
# TODO: Implementar los endpoints HTMX
# ---------------------------------------------------------------------------
#
# Ejemplo de endpoint para obtener horas disponibles:
#
# @router.get("/horas-disponibles", response_class=HTMLResponse)
# async def horas_disponibles(request: Request, fecha: str):
#     """Devuelve un fragmento HTML con las horas disponibles para una fecha."""
#     # Consultar la base de datos para obtener horas ocupadas
#     # Calcular horas libres
#     horas = ["09:00", "10:00", "11:00", "14:00", "15:00"]
#     return templates.TemplateResponse(
#         request=request,
#         name="components/horas_disponibles.html",
#         context={"horas": horas, "fecha": fecha},
#     )
