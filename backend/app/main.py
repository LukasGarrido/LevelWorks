"""
app/main.py
Punto de entrada de la aplicación FastAPI.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin, ModelView

from app.config import settings
from app.core.db.database import init_db, engine
from app.api.v1 import router as api_v1_router

# Importar modelos para que SQLAlchemy los registre en Base.metadata
from app.models import User, Service, Client, Reservation
from app.auth import AdminAuth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa recursos al arrancar y los limpia al apagar."""
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS — necesario porque Astro corre en otro origen (http://localhost:4323)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAdmin Configuración
admin = Admin(
    app,
    engine,
    title="Level Works Panel",
    authentication_backend=AdminAuth()
)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.rol, User.created_at]
    column_searchable_list = [User.username, User.email]
    form_columns = [User.username, User.email, User.hashed_password, User.rol, User.permissions]
    icon = "fa-solid fa-user"


class ServiceAdmin(ModelView, model=Service):
    column_list = [Service.id, Service.name, Service.price, Service.duration_minutes, Service.photo]
    column_searchable_list = [Service.name]
    form_columns = [Service.name, Service.description, Service.price, Service.duration_minutes, Service.photo]
    icon = "fa-solid fa-car"


class ClientAdmin(ModelView, model=Client):
    column_list = [Client.id, Client.name, Client.email, Client.phone]
    column_searchable_list = [Client.name, Client.email]
    icon = "fa-solid fa-users"


class ReservationAdmin(ModelView, model=Reservation):
    column_list = [Reservation.id, Reservation.client, Reservation.service, Reservation.scheduled_at, Reservation.status]
    form_columns = [Reservation.client, Reservation.service, Reservation.scheduled_at, Reservation.status, Reservation.notes]
    form_ajax_refs = {
        "client": {"fields": ("name", "email"), "order_by": "id"},
        "service": {"fields": ("name",), "order_by": "id"},
    }
    icon = "fa-solid fa-calendar-check"


admin.add_view(UserAdmin)
admin.add_view(ServiceAdmin)
admin.add_view(ClientAdmin)
admin.add_view(ReservationAdmin)

# Archivos estáticos (fotos de servicios)
app.mount("/img", StaticFiles(directory="app/img"), name="img")

# Registrar router de la API — todo bajo /api/v1
app.include_router(api_v1_router, prefix="/api/v1")