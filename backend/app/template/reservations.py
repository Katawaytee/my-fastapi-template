import logging
from app.template.model.reservation import ReservationManager
from fastapi import APIRouter

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReservationResource:
    def __init__(self):
        self.reservation_man = ReservationManager()


@router.get("/")
async def reservation_get():
    return {"from": "reservation_get"}