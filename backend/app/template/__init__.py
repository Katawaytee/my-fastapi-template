from fastapi import APIRouter

from app.template import reservations

router = APIRouter()

router.include_router(reservations.router, prefix="/reservations", tags=["reservation"])
