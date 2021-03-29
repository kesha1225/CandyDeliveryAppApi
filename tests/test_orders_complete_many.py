import asyncio
import datetime
import json
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


async def test_couriers_complete_many(cli, session_):
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
                    "region": 9,
                    "delivery_hours": ["17:00-21:30"],
                },
            ]
        },
    )

    courier_id = 2

    resp = await cli.post("/orders/assign", json={"courier_id": courier_id})

    json_data = json.loads(await resp.json())
    assert json_data["orders"] == [{'id': 2}, {'id': 4}, {'id': 6}, {'id': 7}]
    assign_time = json_data["assign_time"]

    current_orders = (
        await session_.execute(select(Order).where(Order.id.in_([2, 4, 6, 7])))
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

    now = datetime.datetime.utcnow()

    for i, order in enumerate(current_orders, start=1):
        now += datetime.timedelta(minutes=5 * i)
        resp = await cli.post(
            "/orders/complete",
            json={
                "courier_id": courier_id,
                "order_id": order.id,
                "complete_time": now.isoformat() + "Z",
            },
        )
        assert json.loads(await resp.json())["order_id"] == order.id
        assert resp.status == 200

        resp = await cli.get(f"/couriers/{courier_id}", json={"courier_id": courier_id})
        courier_data = json.loads(await resp.json())
        if i in [1, 2, 3]:
            assert courier_data.get("rating") is None
        else:
            assert courier_data.get("rating") == 3.96

        resp = await cli.post("/orders/assign", json={"courier_id": courier_id})

    resp = await cli.post("/orders/assign", json={"courier_id": courier_id})
    resp = await cli.post(
        "/orders/complete",
        json={
            "courier_id": courier_id,
            "order_id": 1,
            "complete_time": (now + datetime.timedelta(minutes=40)).isoformat(),
        },
    )

    r = await cli.post(
        "/orders",
        json={
            "data": [
                {
                    "order_id": 8,
                    "weight": 0.5,
                    "region": 12,
                    "delivery_hours": ["09:00-12:00"],
                },
                {
                    "order_id": 9,
                    "weight": 0.2,
                    "region": 9,
                    "delivery_hours": ["17:00-21:30"],
                },
            ]
        },
    )
    json_data = json.loads(await r.json())
    assert json_data["orders"] == [{"id": 8}, {"id": 9}]
    c = await session_.execute(select(Courier).where(Courier.id == courier_id).options(selectinload(Courier.orders)))

    s = 0
    for order in c.fetchall()[0][0].orders:
        s += order.weight

    resp = await cli.post("/orders/assign", json={"courier_id": courier_id})
    json_data = json.loads(await resp.json())
    assert json_data["orders"] == [{"id": 8}, {"id": 9}]
    old_resp = await cli.get(f"/couriers/{courier_id}", json={"courier_id": courier_id})
    old_resp_json = json.loads(await old_resp.json())

    resp = await cli.post(
        "/orders/complete",
        json={
            "courier_id": courier_id,
            "order_id": 8,
            "complete_time": (now + datetime.timedelta(minutes=45)).isoformat(),
        },
    )

    new_resp = await cli.get(f"/couriers/{courier_id}", json={"courier_id": courier_id})
    new_resp_json = json.loads(await new_resp.json())
    assert old_resp_json["rating"] == new_resp_json["rating"]
    assert old_resp_json["earnings"] < new_resp_json["earnings"]

    await session_.commit()

    current_orders = (
        await session_.execute(select(Order).where(Order.id.in_([1, 4, 6, 7])))
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
    assert len(current_courier.delivery_data["regions"]["12"]) == 3
    assert len(current_courier.delivery_data["regions"]["9"]) == 2
    assert len(current_courier.delivery_data["not_completed_regions"]["12"]) == 1

    assert len(current_courier.orders) == 1
