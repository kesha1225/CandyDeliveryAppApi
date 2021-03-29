import asyncio
import datetime
import os

import dotenv
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


async def test_get_couriers(cli, session_):
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
                    "regions": [9, 12, 11],
                    "working_hours": ["09:00-18:00"],
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [12, 22, 24, 33],
                    "working_hours": ["09:00-18:00"],
                },
                {
                    "courier_id": 4,
                    "courier_type": "bike",
                    "regions": [9, 12, 11],
                    "working_hours": ["09:00-18:00"],
                },
            ]
        },
        session=session_,
    )
    r = await cli.post(
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
                    "weight": 9,
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
                {
                    "order_id": 6,
                    "weight": 0.5,
                    "region": 12,
                    "delivery_hours": ["09:00-12:00"],
                },
                {
                    "order_id": 7,
                    "weight": 0.2,
                    "region": 12,
                    "delivery_hours": ["17:00-21:30"],
                },
                {
                    "order_id": 8,
                    "weight": 0.1,
                    "region": 12,
                    "delivery_hours": ["17:00-21:30"],
                },
                {
                    "order_id": 9,
                    "weight": 0.01,
                    "region": 9,
                    "delivery_hours": ["17:00-21:30"],
                },
            ]
        },
    )

    courier_id = 2

    resp = await cli.post("/orders/assign", json={"courier_id": courier_id})

    json_data = await resp.json()
    orders_ids = sorted([order["id"] for order in json_data["orders"]])
    assert orders_ids == [2, 4, 6, 7, 8, 9]

    assign_time = json_data["assign_time"]

    resp2 = await cli.post("/orders/assign", json={"courier_id": courier_id})
    json_data2 = await resp2.json()
    orders_ids = sorted([order["id"] for order in json_data2["orders"]])
    assert orders_ids == [2, 4, 6, 7, 8, 9]

    resp3 = await cli.post("/orders/assign", json={"courier_id": 3})
    json_data3 = await resp3.json()
    orders_ids = sorted([order["id"] for order in json_data3["orders"]])
    assert orders_ids == [1, 3]

    resp = await cli.get(f"/couriers/{courier_id}", json={"courier_id": courier_id})
    courier_data = await resp.json()

    assert courier_data["courier_id"] == 2
    assert courier_data["courier_type"] == "bike"
    assert courier_data["regions"] == [9, 12, 11]
    assert courier_data["working_hours"] == ["09:00-18:00"]
    assert courier_data["earnings"] == 0

    current_orders = (
        await session_.execute(select(Order).where(Order.id.in_([9, 8, 6, 7, 2, 4])))
    ).fetchall()

    current_orders = [order[0] for order in current_orders]

    current_courier: Courier = (
        await session_.execute(
            select(Courier)
            .where(Courier.id == courier_id)
            .options(selectinload(Courier.orders))
        )
    ).first()[0]
    for order in current_orders:
        assert order.courier_id == courier_id
    assert current_courier.orders == current_orders

    now = datetime.datetime.now()

    for i, order in enumerate(current_orders, start=1):
        now += datetime.timedelta(minutes=10 * i)
        resp = await cli.post(
            "/orders/complete",
            json={
                "courier_id": courier_id,
                "order_id": order.id,
                "complete_time": now.isoformat(),
            },
        )
        # resp11 = await cli.post("/orders/assign", json={"courier_id": courier_id})
        # json_data11 = await resp11.json()
        assert resp.status == 200

    await session_.commit()

    current_orders = (
        await session_.execute(select(Order).where(Order.id.in_([9, 8, 6, 7, 2, 4])))
    ).fetchall()
    current_orders = [order[0] for order in current_orders]

    for order in current_orders:
        assert order.courier_id is None
        assert order.completed is True

    current_courier: Courier = (
        await session_.execute(
            select(Courier)
            .where(Courier.id == courier_id)
            .options(selectinload(Courier.orders))
        )
    ).first()[0]
    assert current_courier.earnings == 15000

    assert len(current_courier.delivery_data["regions"]["12"]) == 4
    assert len(current_courier.delivery_data["regions"]["9"]) == 2

    resp = await cli.get(f"/couriers/{courier_id}", json={"courier_id": courier_id})
    courier_data = await resp.json()

    assert courier_data["courier_id"] == 2
    assert courier_data["courier_type"] == "bike"
    assert courier_data["regions"] == [9, 12, 11]
    assert courier_data["working_hours"] == ["09:00-18:00"]
    assert courier_data["rating"] == 2.08
    assert courier_data["earnings"] == 15000

    assert current_courier.orders == []
