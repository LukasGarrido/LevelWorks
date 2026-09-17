from fastapi import APIRouter
from app.api.v1 import services
from app.api.v1 import clients

router = APIRouter()
router.include_router(services.router)
router.include_router(clients.router)