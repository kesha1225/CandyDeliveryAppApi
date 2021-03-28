import asyncio
import datetime
import json
import os

import dotenv

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


async def test_couriers_assign_empty(cli, session_):
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
    r = await cli.post("/orders/assign", json={"courier_id": 2})
    json_data = json.loads(await r.json())
    assert json_data["orders"] == []
    assert json_data.get("assign_time") is None


async def test_couriers_assign(cli, session_):

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
                    "working_hours": [],
                },
                {
                    "courier_id": 4,
                    "courier_type": "foot",
                    "regions": [],
                    "working_hours": ["09:00-18:00"],
                },
                {
                    "courier_id": 5,
                    "courier_type": "car",
                    "regions": [9, 22, 12],
                    "working_hours": ["00:00-23:59"],
                },
                {
                    "courier_id": 6,
                    "courier_type": "bike",
                    "regions": [9],
                    "working_hours": ["09:00-18:00"],
                },
            ]
        },
        session=session_,
    )

    await cli.post(
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
                    "weight": 10,
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

    r = await cli.post("/orders/assign", json={"courier_id": 2})
    json_data = json.loads(await r.json())
    assert len(json_data["orders"]) == 1
    assert json_data["orders"] == [{"id": 2}]
    assert json_data.get("assign_time") is not None
    assert isinstance(json_data["assign_time"], str)
    datetime.datetime.fromisoformat(json_data["assign_time"])

    r = await cli.post("/orders/assign", json={"courier_id": 6})
    json_data = json.loads(await r.json())
    assert json_data["orders"] == []
    assert json_data.get("assign_time") is None

    r = await cli.post("/orders/assign", json={"courier_id": 3})
    json_data = json.loads(await r.json())
    assert json_data["orders"] == []
    assert json_data.get("assign_time") is None

    r = await cli.post("/orders/assign", json={"courier_id": 4})
    json_data = json.loads(await r.json())
    assert json_data["orders"] == []
    assert json_data.get("assign_time") is None

    r = await cli.post("/orders/assign", json={"courier_id": 5})
    json_data = json.loads(await r.json())
    assert len(json_data["orders"]) == 3

    r = await cli.post("/orders/assign", json={"courier_id": 1337})
    assert r.status == 400
    assert r.reason == "Bad Request"
