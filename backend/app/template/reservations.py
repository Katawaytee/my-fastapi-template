import logging

from app.core.response import ResponseException, ResponseModel, ReturnStatus
from app.template.model.reservation import ReservationManager
from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReservationResource:
    def __init__(self):
        self.reservation_man = ReservationManager()

    def get_all_reservation(self):
        """
        get_all_reservation
        """

        stmt = select(
            self.reservation_man.table.c.reservation_id,
            self.reservation_man.table.c.customer_name,
            self.reservation_man.table.c.table_id,
            self.reservation_man.table.c.reservation_time,
            self.reservation_man.table.c.party_size,
        )

        with self.reservation_man.db_engine.connect() as conn:
            result = conn.execute(stmt).fetchall()

        return result


reservation_resource = ReservationResource()


@router.get("/")
async def reservation_list():
    """
    reservation_list
    """

    try:
        reservations = reservation_resource.get_all_reservation()

    except (SQLAlchemyError, DBAPIError):
        logger.error(
            " [reservation_list] Failed to get reservations from the Database."
        )
        raise ResponseException(
            code=status.HTTP_403_FORBIDDEN,
            info="Not allow to add new user!!",
        )

    return ResponseModel(
        status=ReturnStatus.SUCCESS.value,
        content=reservations,
        info=f"{len(reservations)} record(s) retrieved",
    )
