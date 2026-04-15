import logging

from app.core.response import ResponseException, ResponseModel, ReturnStatus
from app.template.model.reservation import ReservationIn, ReservationManager
from fastapi import APIRouter, status
from sqlalchemy import insert, select, update
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

    def add_reservation(self, reservation_in: ReservationIn):
        """
        add_reservation
        """

        value = reservation_in.dict(exclude_none=True)

        stmt = insert(self.reservation_man.table)

        with self.reservation_man.db_engine.begin() as conn:
            result = conn.execute(stmt, value)

        value["reservation_id"] = result.inserted_primary_key[0]

        return value

    def update_single_reservation(
        self, reservation_id: int, reservation_in: ReservationIn
    ):
        """
        update_single_reservation
        """

        value = reservation_in.dict(exclude_none=True)

        stmt = (
            update(self.reservation_man.table)
            .where(self.reservation_man.table.c.reservation_id == reservation_id)
            .values(value)
        )

        with self.reservation_man.db_engine.begin() as conn:
            result = conn.execute(stmt)

        return result.rowcount


reservation_resource = ReservationResource()


@router.get("/")
async def reservation_list():
    """
    reservation_list
    """

    try:
        reservations = reservation_resource.get_all_reservation()

    except (SQLAlchemyError, DBAPIError) as e:
        logger.error(
            f" [reservation_list] Failed to get reservations from the Database. | {e}"
        )
        raise ResponseException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            info="Failed to get reservations from the Database.",
        )

    return ResponseModel(
        status=ReturnStatus.SUCCESS.value,
        content=reservations,
        info=f"{len(reservations)} record(s) retrieved",
    )


@router.post("/")
async def reservation_add(reservation_in: ReservationIn):
    """
    reservation_add
    """

    try:
        result = reservation_resource.add_reservation(reservation_in)

    except (SQLAlchemyError, DBAPIError) as e:
        logger.error(
            f" [reservation_add] Failed to insert reservation to the Database. | {e}"
        )
        raise ResponseException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            info="Failed to insert reservation to the Database.",
        )

    return ResponseModel(
        status=ReturnStatus.SUCCESS.value,
        content=result,
        info="1 record(s) retrieved",
    )


@router.put("/{reservation_id}")
async def reservation_update(reservation_id: int, reservation_in: ReservationIn):
    """
    reservation_update
    """

    try:
        update_count = reservation_resource.update_single_reservation(
            reservation_id=reservation_id,
            reservation_in=reservation_in,
        )

    except (SQLAlchemyError, DBAPIError) as e:
        logger.error(
            f" [reservation_update] Failed to insert reservation to the Database. | {e}"
        )
        raise ResponseException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            info="Failed to update reservation to the Database.",
        )

    return ResponseModel(
        status=ReturnStatus.SUCCESS.value,
        info=f"{update_count} record(s) updated",
    )
