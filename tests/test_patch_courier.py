import asyncio
import os

import dotenv
from aiohttp.test_utils import TestClient

from candy_delivery_app.db.context_uri import DB_URI
from candy_delivery_app.db.db import update_base, session
from candy_delivery_app.db.models.couriers import Courier

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
                    "regions": [12, 22, 24, 33],
                    "working_hours": ["09:00-18:00"],
                },
            ]
        },
        session=session_,
    )
    couriers = (await session_.execute("SELECT * FROM couriers")).fetchall()

    assert couriers[2].regions == [12, 22, 24, 33]
    assert couriers[2].working_hours == ["09:00-18:00"]
    assert couriers[2].working_hours_timedeltas == [
        {"first_time": 32400, "second_time": 64800}
    ]

    await Courier.patch_courier(
        session=session_,
        courier_id=3,
        new_data={
            "regions": [12, 9, 1, 22],
            "working_hours": ["11:00-17:59", "19:00-20:00"],
        },
    )
    couriers = (await session_.execute("SELECT * FROM couriers")).fetchall()
    assert couriers[2].regions == [12, 9, 1, 22]
    assert couriers[2].working_hours == ["11:00-17:59", "19:00-20:00"]
    assert couriers[2].working_hours_timedeltas == [
        {"first_time": 39600, "second_time": 64740},
        {"first_time": 68400, "second_time": 72000},
    ]
