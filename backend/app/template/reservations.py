import logging
from typing import Optional

from app.core.response import (
    ResponseException,
    ResponseModel,
    ReturnStatus,
    SearchResponseModel,
)
from app.template.helpers.sqlalchemy import build_sort_expression
from app.template.model.reservation import (
    ReservationBulkAddIn,
    ReservationBulkUpdateIn,
    ReservationIn,
    ReservationManager,
    ReservationUpdateIn,
)
from fastapi import APIRouter, status
from sqlalchemy import bindparam, delete, func, insert, select, update
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReservationResource:
    def __init__(self):
        self.reservation_man = ReservationManager()

    def get_all_reservation(
        self,
        search_query: Optional[str] = None,
        order_by: Optional[str] = None,
        page: int = 0,
        page_size: Optional[int] = None,
    ):
        """
        Return a list of reservations.

        Parameters
        ----------
        - `search_query` (str)
            A search keyword to search by the customer name.
        - `order_by` (str)
            The field and direction to sort the results (e.g., "customer_name asc").
        - `page` (int)
            The current page number for pagination.
        - `page_size` (int)
            The number of reservations to display per page.

        Returns
        -------
        **tuple**
        - `reservation_count` (int)
        - `result` (list[object])
            - `reservation_id` (int)
            - `customer_name` (str)
            - `table_id` (int)
            - `reservation_time` (datetime)
            - `party_size` (int)
        """

        count_stmt = select(func.count()).select_from(self.reservation_man.table)

        stmt = select(
            self.reservation_man.table.c.reservation_id,
            self.reservation_man.table.c.customer_name,
            self.reservation_man.table.c.table_id,
            self.reservation_man.table.c.reservation_time,
            self.reservation_man.table.c.party_size,
        )

        # Search
        if search_query:
            search_exp = self.reservation_man.table.c.customer_name.contains(
                search_query
            )

            count_stmt = count_stmt.where(search_exp)
            stmt = stmt.where(search_exp)

        # Sorting
        if order_by:
            valid_sort_columns = {
                "reservation_id": self.reservation_man.table.c.reservation_id,
                "customer_name": self.reservation_man.table.c.customer_name,
                "table_id": self.reservation_man.table.c.table_id,
                "reservation_time": self.reservation_man.table.c.reservation_time,
                "party_size": self.reservation_man.table.c.party_size,
            }

            sort_expression = build_sort_expression(
                order_by=order_by,
                valid_columns=valid_sort_columns,
                default_field="reservation_id",
            )

            stmt = stmt.order_by(sort_expression)

        # Pagination
        if page_size:
            stmt = stmt.limit(page_size).offset(page * page_size)

        with self.reservation_man.db_engine.connect() as conn:
            total_count = conn.execute(count_stmt).scalar() or 0
            result = conn.execute(stmt).fetchall()

        return total_count, result

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

    def delete_single_reservation(self, reservation_id: int):
        """
        delete_single_reservation
        """

        stmt = delete(self.reservation_man.table).where(
            self.reservation_man.table.c.reservation_id == reservation_id
        )

        with self.reservation_man.db_engine.begin() as conn:
            result = conn.execute(stmt)

        return result.rowcount

    def add_multiple_reservations(self, reservations: list[ReservationIn]):
        """
        add_multiple_reservations
        """

        # Convert to bulk insertable form
        reservation_list = [obj.dict() for obj in reservations]

        stmt = insert(self.reservation_man.table)

        with self.reservation_man.db_engine.begin() as conn:
            result = conn.execute(stmt, reservation_list)

        return result.rowcount

    def update_multiple_reservations(self, reservations: list[ReservationUpdateIn]):
        """
        update_multiple_reservations
        """

        # Convert to bulk updatable form
        reservation_list = []
        for obj in reservations:
            data = obj.dict()
            data["b_reservation_id"] = data.pop("reservation_id")
            reservation_list.append(data)

        stmt = update(self.reservation_man.table).where(
            self.reservation_man.table.c.reservation_id == bindparam("b_reservation_id")
        )

        with self.reservation_man.db_engine.begin() as conn:
            result = conn.execute(stmt, reservation_list)

            # Rollback all the updates
            # if some of provided id does not exist
            if result.rowcount != len(reservation_list):
                raise ValueError("Some of the target reservation do not exist.")

        return result.rowcount


reservation_resource = ReservationResource()


@router.get("/")
async def reservation_list(
    search_query: Optional[str] = None,
    order_by: Optional[str] = None,
    page: int = 0,
    page_size: Optional[int] = None,
):
    """
    reservation_list
    """

    try:
        count, reservations = reservation_resource.get_all_reservation(
            search_query=search_query,
            order_by=order_by,
            page=page,
            page_size=page_size,
        )

    except (SQLAlchemyError, DBAPIError) as e:
        logger.error(
            f" [reservation_list] Failed to get reservations from the Database. | {e}"
        )
        raise ResponseException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            info="Failed to get reservations from the Database.",
        )

    return SearchResponseModel(
        status=ReturnStatus.SUCCESS.value,
        count=count,
        data=reservations,
        page=page,
        page_size=page_size,
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


@router.post("/bulk")
async def reservation_bulk_add(bulk_add_in: ReservationBulkAddIn):
    """
    reservation_bulk_add
    """

    try:
        insert_count = reservation_resource.add_multiple_reservations(
            reservations=bulk_add_in.reservations,
        )

    except (SQLAlchemyError, DBAPIError) as e:
        logger.error(
            f" [reservation_bulk_add] Failed to  bulk insert reservation to the Database. | {e}"
        )
        raise ResponseException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            info="Failed to bulk insert reservation to the Database.",
        )

    return ResponseModel(
        status=ReturnStatus.SUCCESS.value,
        info=f"{insert_count} record(s) retrieved",
    )


@router.put("/bulk")
async def reservation_bulk_update(bulk_update_in: ReservationBulkUpdateIn):
    """
    reservation_update_add
    """

    try:
        update_count = reservation_resource.update_multiple_reservations(
            reservations=bulk_update_in.reservations,
        )

    except (SQLAlchemyError, DBAPIError, ValueError) as e:
        logger.error(
            f" [reservation_bulk_update] Failed to  bulk update reservation to the Database. | {e}"
        )
        raise ResponseException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            info="Failed to bulk update reservation to the Database.",
        )

    return ResponseModel(
        status=ReturnStatus.SUCCESS.value,
        info=f"{update_count} record(s) retrieved",
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


@router.delete("/{reservation_id}")
async def reservation_delete(reservation_id: int):
    """
    reservation_delete
    """

    try:
        delete_count = reservation_resource.delete_single_reservation(reservation_id)

    except (SQLAlchemyError, DBAPIError) as e:
        logger.error(
            f" [reservation_delete] Failed to insert reservation to the Database. | {e}"
        )
        raise ResponseException(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            info="Failed to delete reservation from the Database.",
        )

    return ResponseModel(
        status=ReturnStatus.SUCCESS.value,
        info=f"{delete_count} record(s) deleted",
    )
