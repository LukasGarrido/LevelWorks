"""
app/main.py
Punto de entrada de la aplicación FastAPI.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin, ModelView

from app.config import get_settings
from app.core.db.database import init_db, engine
from app.routes import views, api

# Importar modelos para que SQLAlchemy los registre en Base.metadata
from app.models import User, Service, Client, Reservation
from app.auth import AdminAuth



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
        "client": {
            "fields": ("name", "email"),
            "order_by": "id",
        },
        "service": {
            "fields": ("name",),
            "order_by": "id",
        }
    }
    icon = "fa-solid fa-calendar-check"

admin.add_view(UserAdmin)
admin.add_view(ServiceAdmin)
admin.add_view(ClientAdmin)
admin.add_view(ReservationAdmin)

# Archivos estáticos
app.mount("/img", StaticFiles(directory="app/img"), name="img")

# Registrar routers
app.include_router(views.router)
app.include_router(api.router)
