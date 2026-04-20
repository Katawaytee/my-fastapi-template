import pytest
from app.core.response import ReturnStatus
from app.template.model.reservation import (
    ReservationBulkAddIn,
    ReservationBulkDeleteIn,
    ReservationBulkUpdateIn,
    ReservationIn,
)
from app.template.reservations import (
    reservation_add,
    reservation_bulk_add,
    reservation_bulk_delete,
    reservation_bulk_update,
    reservation_delete,
    reservation_list,
    reservation_update,
)

# ---------- ADD RESERVATION ---------- #
MOCK_RESERVATION_IN = ReservationIn(
    customer_name="Customer One",
    party_size=4,
    reservation_time="2026-11-17T16:59:00.000Z",
    table_id=3,
)


@pytest.mark.asyncio
async def test_reservation_add():
    res = await reservation_add(reservation_in=MOCK_RESERVATION_IN)

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.info == "1 record(s) inserted"

    assert res.content["reservation_id"] is not None
    assert res.content["customer_name"] == MOCK_RESERVATION_IN.customer_name
    assert res.content["party_size"] == MOCK_RESERVATION_IN.party_size
    assert res.content["reservation_time"] == MOCK_RESERVATION_IN.reservation_time
    assert res.content["table_id"] == MOCK_RESERVATION_IN.table_id

    # setup for followed test cases
    global created_reservation_id
    created_reservation_id = res.content["reservation_id"]
