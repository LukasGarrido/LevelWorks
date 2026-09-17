from fastapi import APIRouter
from app.api.v1 import services
from app.api.v1 import clients
from app.api.v1 import users
from app.api.v1 import reservations
from app.api.v1 import auth

router = APIRouter()
router.include_router(auth.router)
router.include_router(services.router)
router.include_router(clients.router)
router.include_router(users.router)
router.include_router(reservations.router)