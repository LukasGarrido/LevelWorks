"""
app/main.py
Punto de entrada de la aplicación FastAPI.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from app.routes import views, api


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
# Archivos estáticos (CSS, JS, imágenes)
# ---------------------------------------------------------------------------
# Descomenta la siguiente línea cuando crees la carpeta app/static/
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---------------------------------------------------------------------------
# Registrar routers
# ---------------------------------------------------------------------------
app.include_router(views.router)
app.include_router(api.router)
