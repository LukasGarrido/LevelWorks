"""
app/main.py
Punto de entrada de la aplicación FastAPI.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin, ModelView

from app.config import get_settings
from app.database import init_db, engine
from app.routes import views, api
# Importar modelos para que SQLAlchemy los registre en Base.metadata
from app import models



settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa recursos al arrancar y los limpia al apagar."""
    # Startup: crear tablas en la base de datos
    await init_db()
    yield
    # Shutdown: aquí se pueden cerrar conexiones si es necesario


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# SQLAdmin Configuración
# ---------------------------------------------------------------------------
admin = Admin(app, engine)

class ServiceAdmin(ModelView, model=models.Service):
    column_list = [models.Service.id, models.Service.name, models.Service.price, models.Service.duration_minutes]
    column_searchable_list = [models.Service.name]
    form_columns = [models.Service.name, models.Service.description, models.Service.price, models.Service.duration_minutes]
    icon = "fa-solid fa-car"

class ClientAdmin(ModelView, model=models.Client):
    column_list = [models.Client.id, models.Client.name, models.Client.email, models.Client.phone]
    column_searchable_list = [models.Client.name, models.Client.email]
    icon = "fa-solid fa-users"

class ReservationAdmin(ModelView, model=models.Reservation):
    column_list = [models.Reservation.id, models.Reservation.client_id, models.Reservation.service_id, models.Reservation.scheduled_at, models.Reservation.status]
    icon = "fa-solid fa-calendar-check"

admin.add_view(ServiceAdmin)
admin.add_view(ClientAdmin)
admin.add_view(ReservationAdmin)

# ---------------------------------------------------------------------------
# Archivos estáticos (CSS, JS, imágenes)
# ---------------------------------------------------------------------------
# Descomenta la siguiente línea cuando crees la carpeta app/static/
# app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/img", StaticFiles(directory="app/img"), name="img")

# ---------------------------------------------------------------------------
# Registrar routers
# ---------------------------------------------------------------------------
app.include_router(views.router)
app.include_router(api.router)
