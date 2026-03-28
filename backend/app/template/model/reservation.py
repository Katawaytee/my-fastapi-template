from app.core.database import DBManager


class ReservationManager(DBManager):
    def __init__(self):
        super().__init__("reservation", None)
