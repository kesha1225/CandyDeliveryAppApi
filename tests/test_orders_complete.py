import asyncio
import datetime
import json
import os

import dotenv
from sqlalchemy import select
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


async def test_couriers_complete(cli, session_):
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

    courier_id = 2

    resp = await cli.post("/orders/assign", json={"courier_id": courier_id})

    json_data = json.loads(await resp.json())
    assign_time = json_data["assign_time"]
    order_id = json_data["orders"][0]["id"]

    current_order: Order = (
        await session_.execute(select(Order).where(Order.id == order_id))
    ).first()[0]

    assert current_order.completed is False

    assert current_order.courier_id == courier_id

    current_courier: Courier = (
        await session_.execute(
            select(Courier)
            .where(Courier.id == courier_id)
            .options(selectinload(Courier.orders))
        )
    ).first()[0]

    assert current_order.courier_id == courier_id
    assert current_courier.orders == [current_order]

    now = datetime.datetime.now()
    resp = await cli.post(
        "/orders/complete",
        json={
            "courier_id": courier_id,
            "order_id": order_id,
            "complete_time": now.isoformat(),
        },
    )
    await session_.commit()
    json_data = json.loads(await resp.json())

    current_order: Order = (
        await session_.execute(select(Order).where(Order.id == order_id))
    ).first()[0]

    current_courier: Courier = (
        await session_.execute(
            select(Courier)
            .where(Courier.id == courier_id)
            .options(selectinload(Courier.orders))
        )
    ).first()[0]

    delivery_time = (
        now.timestamp() - datetime.datetime.fromisoformat(assign_time).timestamp()
    )
    assert current_courier.delivery_data["regions"]["9"][0] == delivery_time
    assert current_courier.last_delivery_time == now.timestamp()
    assert current_order.courier_id is None
    assert current_order.completed is True
    assert current_courier.orders == []

    assert json_data["order_id"] == order_id

    resp = await cli.post(
        "/orders/complete",
        json={
            "courier_id": 1337,
            "order_id": order_id,
            "complete_time": now.isoformat(),
        },
    )
    assert resp.status == 400
    assert resp.reason == "Bad Request"

    resp = await cli.post(
        "/orders/complete",
        json={
            "courier_id": 2,
            "order_id": order_id,
            "complete_time": now.isoformat(),
        },
    )
    assert resp.status == 200
    json_data = json.loads(await resp.json())
    assert json_data["order_id"] == order_id

    resp = await cli.post(
        "/orders/complete",
        json={
            "courier_id": 2,
            "order_id": order_id,
            "complete_time": "fds",
        },
    )
    assert resp.status == 400

    resp = await cli.post(
        "/orders/complete",
        json={
            "courier_id": 2,
            "order_id": order_id,
            "complete_time": (now + datetime.timedelta(minutes=423)).isoformat(),
        },
    )
    assert resp.status == 400

    resp = await cli.post(
        "/orders/complete",
        json={
            "courier_id": 2,
            "order_id": 31312,
            "complete_time": now.isoformat(),
        },
    )
    assert resp.status == 400
