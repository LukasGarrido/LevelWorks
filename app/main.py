"""
app/main.py
Punto de entrada de la aplicación FastAPI.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin, ModelView
from wtforms import FileField

from app.config import get_settings
from app.database import init_db, engine
from app.routes import views, api
# Importar modelos para que SQLAlchemy los registre en Base.metadata
from app import models

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
    title="Xperience Panel",
    authentication_backend=AdminAuth()
)

class UserAdmin(ModelView, model=models.User):
    column_list = [models.User.id, models.User.username, models.User.email, models.User.rol, models.User.created_at]
    column_searchable_list = [models.User.username, models.User.email]
    form_columns = [models.User.username, models.User.email, models.User.hashed_password, models.User.rol, models.User.permissions]
    icon = "fa-solid fa-user"

class ServiceAdmin(ModelView, model=models.Service):
    column_list = [models.Service.id, models.Service.name, models.Service.price, models.Service.duration_minutes, models.Service.photo]
    column_searchable_list = [models.Service.name]
    form_columns = [models.Service.name, models.Service.description, models.Service.price, models.Service.duration_minutes, models.Service.photo]
    form_overrides = dict(photo=FileField)
    icon = "fa-solid fa-car"

    async def on_model_change(self, data, model, is_created, request):
        photo = data.get("photo")
        if photo and getattr(photo, "filename", None):
            filename = photo.filename
            content = await photo.read()
            os.makedirs("app/img", exist_ok=True)
            file_path = os.path.join("app", "img", filename)
            with open(file_path, "wb") as f:
                f.write(content)
            data["photo"] = f"/img/{filename}"
        else:
            if not is_created:
                data.pop("photo", None)
            else:
                data["photo"] = None

class ClientAdmin(ModelView, model=models.Client):
    column_list = [models.Client.id, models.Client.name, models.Client.email, models.Client.phone]
    column_searchable_list = [models.Client.name, models.Client.email]
    icon = "fa-solid fa-users"

class ReservationAdmin(ModelView, model=models.Reservation):
    column_list = [models.Reservation.id, models.Reservation.client, models.Reservation.service, models.Reservation.scheduled_at, models.Reservation.status]
    form_columns = [models.Reservation.client, models.Reservation.service, models.Reservation.scheduled_at, models.Reservation.status, models.Reservation.notes]
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
