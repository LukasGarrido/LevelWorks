from fastapi import APIRouter
from app.api.v1 import services

router = APIRouter()
router.include_router(services.router)