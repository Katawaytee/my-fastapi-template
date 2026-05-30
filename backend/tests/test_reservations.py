from datetime import datetime

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
    reservation_time=datetime(2026, 11, 17, 16, 59),
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


# ---------- BULK ADD RESERVATION ---------- #
MOCK_RESERVATION_BULK_ADD_IN = ReservationBulkAddIn(
    reservations=[
        ReservationIn(
            customer_name="Customer Two",
            party_size=4,
            reservation_time="2026-11-17T16:59:00.000Z",
            table_id=4,
        ),
        ReservationIn(
            customer_name="Customer Three",
            party_size=4,
            reservation_time="2026-11-17T16:59:00.000Z",
            table_id=2,
        ),
    ]
)


@pytest.mark.asyncio
async def test_reservation_bulk_add():
    res = await reservation_bulk_add(bulk_add_in=MOCK_RESERVATION_BULK_ADD_IN)

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.info == "2 record(s) inserted"


# ---------- LIST RESERVATION ---------- #
@pytest.mark.asyncio
async def test_reservation_list_default_params():
    res = await reservation_list()

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.count == 3
    assert res.page == 0
    assert res.page_size is None

    data = res.data

    assert data[0].reservation_id == created_reservation_id
    assert data[0].customer_name == MOCK_RESERVATION_IN.customer_name
    assert data[0].party_size == MOCK_RESERVATION_IN.party_size
    assert data[0].reservation_time == MOCK_RESERVATION_IN.reservation_time
    assert data[0].table_id == MOCK_RESERVATION_IN.table_id

    # setup for followed test cases
    global bulk_created_reservation_id
    bulk_created_reservation_id = [
        item.reservation_id
        for item in data
        if item.reservation_id != created_reservation_id
    ]


@pytest.mark.asyncio
async def test_reservation_list_search_query():
    res = await reservation_list(search_query="Two")

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.count == 1
    assert len(res.data) == 1

    assert "Two" in res.data[0].customer_name


@pytest.mark.asyncio
async def test_reservation_list_order_by():
    res = await reservation_list(order_by="reservation_id desc")

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.count == 3
    assert len(res.data) == 3

    for i in range(1, 3):
        assert res.data[i - 1].reservation_id > res.data[i].reservation_id


@pytest.mark.asyncio
async def test_reservation_list_pagination():
    res = await reservation_list(page=0, page_size=2)

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.count == 3
    assert res.page == 0
    assert res.page_size == 2

    assert len(res.data) == 2


@pytest.mark.asyncio
async def test_reservation_list_all_params():
    res = await reservation_list(
        search_query="Customer T",
        order_by="reservation_id desc",
        page=0,
        page_size=5,
    )

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.count == 2
    assert res.page == 0
    assert res.page_size == 5

    assert len(res.data) == 2

    assert res.data[0].reservation_id > res.data[1].reservation_id


# ---------- UPDATE RESERVATION ---------- #
MOCK_RESERVATION_UPDATE_IN = ReservationIn(
    customer_name="Customer One Updated",
    party_size=6,
    reservation_time=datetime(2026, 11, 18, 18, 0),
    table_id=5,
)


@pytest.mark.asyncio
async def test_reservation_update():
    res = await reservation_update(
        reservation_id=created_reservation_id,
        reservation_in=MOCK_RESERVATION_UPDATE_IN,
    )

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.info == "1 record(s) updated"

    # Verify the update by calling reservation_list
    list_res = await reservation_list(search_query="Customer One Updated")
    assert list_res.status == ReturnStatus.SUCCESS.value
    assert list_res.count == 1
    assert len(list_res.data) == 1

    updated_data = list_res.data[0]
    assert updated_data.reservation_id == created_reservation_id
    assert updated_data.customer_name == MOCK_RESERVATION_UPDATE_IN.customer_name
    assert updated_data.party_size == MOCK_RESERVATION_UPDATE_IN.party_size
    assert updated_data.reservation_time == MOCK_RESERVATION_UPDATE_IN.reservation_time
    assert updated_data.table_id == MOCK_RESERVATION_UPDATE_IN.table_id


@pytest.mark.asyncio
async def test_reservation_update_not_found():
    res = await reservation_update(
        reservation_id=99999,
        reservation_in=MOCK_RESERVATION_UPDATE_IN,
    )

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.info == "0 record(s) updated"

