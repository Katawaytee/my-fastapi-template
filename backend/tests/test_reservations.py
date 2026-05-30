from datetime import datetime

import pytest
from app.core.response import ResponseException, ReturnStatus
from app.template.model.reservation import (
    ReservationBulkAddIn,
    ReservationBulkDeleteIn,
    ReservationBulkUpdateIn,
    ReservationIn,
    ReservationUpdateIn,
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


@pytest.fixture
def mock_reservation_bulk_update_in():
    return ReservationBulkUpdateIn(
        reservations=[
            ReservationUpdateIn(
                reservation_id=bulk_created_reservation_id[0],
                customer_name="Customer Two Updated",
                party_size=8,
                reservation_time=datetime(2026, 11, 19, 19, 0),
                table_id=6,
            ),
            ReservationUpdateIn(
                reservation_id=bulk_created_reservation_id[1],
                customer_name="Customer Three Updated",
                party_size=10,
                reservation_time=datetime(2026, 11, 20, 20, 0),
                table_id=7,
            ),
        ]
    )


@pytest.fixture
def mock_reservation_bulk_delete_in():
    return ReservationBulkDeleteIn(reservation_ids=bulk_created_reservation_id)


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


# ---------- BULK UPDATE RESERVATION ---------- #
MOCK_RESERVATION_BULK_UPDATE_NOT_FOUND_IN = ReservationBulkUpdateIn(
    reservations=[
        ReservationUpdateIn(
            reservation_id=99999,
            customer_name="Non Existent Customer",
            party_size=4,
            reservation_time=datetime(2026, 11, 21, 21, 0),
            table_id=8,
        )
    ]
)


@pytest.mark.asyncio
async def test_reservation_bulk_update(mock_reservation_bulk_update_in):
    assert len(bulk_created_reservation_id) == 2

    res = await reservation_bulk_update(bulk_update_in=mock_reservation_bulk_update_in)

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.info == "2 record(s) updated"

    # Verify the updates using reservation_list
    list_res = await reservation_list(search_query="Updated")
    assert list_res.status == ReturnStatus.SUCCESS.value
    # It should find 3 updated items:
    # - Customer One Updated
    # - Customer Two Updated
    # - Customer Three Updated
    assert list_res.count == 3


@pytest.mark.asyncio
async def test_reservation_bulk_update_not_found():
    with pytest.raises(ResponseException) as exc_info:
        await reservation_bulk_update(
            bulk_update_in=MOCK_RESERVATION_BULK_UPDATE_NOT_FOUND_IN
        )

    assert exc_info.value.code == 500
    assert exc_info.value.info == "Failed to bulk update reservation to the Database."


# ---------- DELETE RESERVATION ---------- #
@pytest.mark.asyncio
async def test_reservation_delete():
    res = await reservation_delete(reservation_id=created_reservation_id)

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.info == "1 record(s) deleted"

    # Verify it is deleted
    list_res = await reservation_list(search_query="Customer One Updated")
    assert list_res.status == ReturnStatus.SUCCESS.value
    assert list_res.count == 0


@pytest.mark.asyncio
async def test_reservation_delete_not_found():
    res = await reservation_delete(reservation_id=99999)

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.info == "0 record(s) deleted"


# ---------- BULK DELETE RESERVATION ---------- #
MOCK_RESERVATION_BULK_DELETE_NOT_FOUND_IN = ReservationBulkDeleteIn(
    reservation_ids=[99998, 99999]
)


@pytest.mark.asyncio
async def test_reservation_bulk_delete(mock_reservation_bulk_delete_in):
    assert len(bulk_created_reservation_id) == 2

    res = await reservation_bulk_delete(bulk_delete_in=mock_reservation_bulk_delete_in)

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.info == "2 record(s) deleted"

    # Verify they are deleted
    list_res = await reservation_list()
    assert list_res.status == ReturnStatus.SUCCESS.value
    assert list_res.count == 0


@pytest.mark.asyncio
async def test_reservation_bulk_delete_not_found():
    res = await reservation_bulk_delete(
        bulk_delete_in=MOCK_RESERVATION_BULK_DELETE_NOT_FOUND_IN
    )

    assert res.status == ReturnStatus.SUCCESS.value
    assert res.info == "0 record(s) deleted"
