import asyncio
import json
import os

import dotenv

from candy_delivery_app.db.context_uri import DB_URI
from candy_delivery_app.db.db import update_base, session

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


async def test_orders_post_good(cli, session_):
    await update_base()
    response = await cli.post(
        "/orders",
        json={
            "data": [
                {
                    "order_id": 1,
                    "weight": 3,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"],
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 9,
                    "delivery_hours": ["09:00-18:00"],
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"],
                },
                {
                    "order_id": 4,
                    "weight": 5,
                    "region": 12,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30", "22:00-23:59"],
                },
            ]
        },
    )

    assert response.status == 201
    orders = (await session_.execute("SELECT * FROM orders")).fetchall()
    assert orders[0].id == 1
    assert orders[0].weight == 3.0
    assert orders[0].region == 12
    assert orders[0].delivery_hours == ["09:00-18:00"]
    assert orders[0].delivery_hours_timedeltas == [
        {"first_time": 32400, "second_time": 64800}
    ]
    assert orders[0].assign_time is None
    assert orders[0].completed is False
    assert orders[0].courier_id is None
    assert orders[0].cost is None


async def test_orders_post_bad(cli, session_):
    await update_base()
    response = await cli.post(
        "/orders",
        json={
            "data": [
                {
                    "order_id": 1,
                    "weight": 3,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"],
                },
                {
                    "order_id": 2,
                    "weight": -15,
                    "region": 9,
                    "delivery_hours": ["09:00-18:00"],
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:70-12:00", "16:00-21:30"],
                },
                {
                    "order_id": 4,
                    "weight": 5,
                    "region": 12,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30", "22:00-23:59"],
                },
            ]
        },
    )

    assert response.status == 400
    json_data = json.loads(await response.json())
    assert json_data["validation_error"]["orders"] == [{"id": 2}, {"id": 3}]
    assert json_data["validation_error"]["errors_data"] == [
        {
            "location": ["data", 1, "weight"],
            "msg": "value is not a valid float",
            "type": "type_error.float",
        },
        {
            "location": ["data", 1, "weight"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt",
        },
        {
            "location": ["data", 2, "delivery_hours"],
            "msg": "Invalid date - 09:70-12:00",
            "type": "value_error",
        },
    ]
