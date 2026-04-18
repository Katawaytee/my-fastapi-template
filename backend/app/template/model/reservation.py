from datetime import datetime
from typing import Optional

from app.core.database import DBManager
from pydantic import BaseModel


class ReservationIn(BaseModel):
    customer_name: Optional[str]
    table_id: Optional[int]
    reservation_time: Optional[datetime]
    party_size: Optional[int]


class Reservation(ReservationIn):
    reservation_id: int
    create_time: datetime
    update_time: datetime


class ReservationBulkAddIn(BaseModel):
    reservations: list[ReservationIn]


class ReservationManager(DBManager):
    def __init__(self):
        super().__init__("reservation", None)
