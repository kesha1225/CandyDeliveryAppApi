import asyncio
import os

import dotenv
from aiohttp.test_utils import TestClient
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from candy_delivery_app.db.context_uri import DB_URI
from candy_delivery_app.db.db import update_base, session
from candy_delivery_app.db.models.couriers import Courier
from candy_delivery_app.db.models.orders import Order

dotenv.load_dotenv()

DB_URI.set(os.getenv("TEST_DB_URI"))

import pytest
from aiohttp import web

from candy_delivery_app.api import couriers_router, orders_router


@pytest.fixture
def loop():
    return asyncio.get_event_loop()


@pytest.fixture
def cli(loop, aiohttp_client):
    app = web.Application()
    app.add_routes(couriers_router)
    app.add_routes(orders_router)
    return loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
async def session_():
    async_session = session()

    yield async_session

    await async_session.close()


async def test_couriers_patch(cli, session_):
    await update_base()
    await Courier.create_couriers(
        json_data={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1],
                    "working_hours": ["11:35-14:05", "09:00-11:00"],
                },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [9],
                    "working_hours": ["09:00-18:00"],
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [9, 12, 22, 24, 33, 13],
                    "working_hours": ["09:00-18:00"],
                },
            ]
        },
        session=session_,
    )
    couriers = (await session_.execute("SELECT * FROM couriers")).fetchall()

    assert couriers[2].regions == [9, 12, 22, 24, 33, 13]
    assert couriers[2].working_hours == ["09:00-18:00"]
    assert couriers[2].working_hours_timedeltas == [
        {"first_time": 32400, "second_time": 64800}
    ]

    await Order.create_orders(
        session=session_,
        json_data={
            "data": [
                {
                    "order_id": 1,
                    "weight": 3,
                    "region": 9,
                    "delivery_hours": ["09:00-18:00"],
                },
                {
                    "order_id": 2,
                    "weight": 1,
                    "region": 9,
                    "delivery_hours": ["09:00-18:00"],
                },
                {
                    "order_id": 3,
                    "weight": 16,
                    "region": 22,
                    "delivery_hours": ["16:00-21:30"],
                },
                {
                    "order_id": 4,
                    "weight": 3,
                    "region": 12,
                    "delivery_hours": ["17:00-21:30"],
                },
                {
                    "order_id": 5,
                    "weight": 0.3,
                    "region": 13,
                    "delivery_hours": ["17:00-21:30"],
                },
            ]
        },
    )

    resp = await cli.post("/orders/assign", json={"courier_id": 3})

    courier = (
        await session_.execute(
            select(Courier).where(Courier.id == 3).options(selectinload(Courier.orders))
        )
    ).first()[0]
    assert len(courier.orders) == 5

    await Courier.patch_courier(
        session=session_,
        courier_id=3,
        new_data={
            "regions": [12, 9, 1, 22],
            "working_hours": ["18:00-21:00"],
        },
    )

    courier = (
        await session_.execute(
            select(Courier).where(Courier.id == 3).options(selectinload(Courier.orders))
        )
    ).first()[0]
    assert len(courier.orders) == 2
    assert courier.orders[0].id == 3
    assert courier.regions == [12, 9, 1, 22]
    assert courier.working_hours == ["18:00-21:00"]
    assert courier.working_hours_timedeltas == [
        {"first_time": 64800, "second_time": 75600}
    ]

    await Courier.patch_courier(
        session=session_,
        courier_id=3,
        new_data={"courier_type": "bike"},
    )

    courier = (
        await session_.execute(
            select(Courier).where(Courier.id == 3).options(selectinload(Courier.orders))
        )
    ).first()[0]
    assert len(courier.orders) == 1
    assert courier.orders[0].id == 4

    orders = (await session_.execute("SELECT * FROM orders")).fetchall()
    for order in orders:
        if order.id == 4:
            assert order.courier_id == 3
        else:
            assert order.courier_id is None
