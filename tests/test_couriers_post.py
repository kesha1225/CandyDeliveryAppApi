import asyncio
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


async def test_couriers_post_good(cli, session_):
    await update_base()
    response = await cli.post(
        "/couriers",
        json={
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
    )
    couriers = (await session_.execute("SELECT * FROM couriers")).fetchall()
    assert couriers[0].id == 1
    assert couriers[0].regions == [1]
    assert couriers[0].courier_type == "FOOT"
    assert couriers[0].working_hours == ["11:35-14:05", "09:00-11:00"]
    assert couriers[0].working_hours_timedeltas == [
        {"first_time": 41700, "second_time": 50700},
        {"first_time": 32400, "second_time": 39600},
    ]
    assert couriers[0].earnings == 0
    assert couriers[0].rating is None
    assert couriers[0].last_delivery_time is None
    assert couriers[0].delivery_data is None

    assert couriers[1].id == 2
    assert couriers[1].regions == [9]
    assert couriers[1].courier_type == "BIKE"
    assert couriers[1].working_hours == ["09:00-18:00"]
    assert couriers[1].working_hours_timedeltas == [
        {"first_time": 32400, "second_time": 64800}
    ]
    assert couriers[1].earnings == 0
    assert couriers[1].rating is None

    assert response.status == 201


async def test_couriers_post_bad(cli, session_):
    await update_base()

    response = await cli.post(
        "/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "fot",
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
    )
    json_response = await response.json()

    assert json_response["validation_error"]["couriers"] == [{"id": 1}]
    assert json_response["validation_error"]["errors_data"][0]["location"] == [
        "data",
        0,
        "courier_type",
    ]

    assert response.status == 400

    response = await cli.post(
        "/couriers",
        json={
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
                    "working_hours": ["24:00-18:00"],
                },
            ]
        },
    )
    json_response = await response.json()
    assert json_response["validation_error"]["couriers"] == [{"id": 3}]
    assert json_response["validation_error"]["errors_data"][0]["location"] == [
        "data",
        2,
        "working_hours",
    ]
    assert response.status == 400

    response = await cli.post(
        "/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1],
                    "working_hours": ["11:35-shue", "09:00-11:00"],
                },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [9, -3],
                    "working_hours": ["09:00-18:00"],
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [12, "22", 24, 33],
                    "working_hours": ["11:00-18:00"],
                },
            ]
        },
    )
    json_response = await response.json()
    assert json_response["validation_error"]["couriers"] == [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]
    assert (
        json_response["validation_error"]["errors_data"][0]["msg"]
        == "Invalid date - 11:35-shue"
    )
    assert (
        json_response["validation_error"]["errors_data"][1]["type"]
        == "value_error.number.not_ge"
    )
    assert json_response["validation_error"]["errors_data"][2]["location"] == [
        "data",
        2,
        "regions",
        1,
    ]

    response = await cli.post(
        "/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1],
                    "working_hours": ["11:35-12:00", "09:00-11:00"],
                },
            ]
        },
    )
    json_response = await response.json()
    assert json_response == {"couriers": [{"id": 1}]}

    response = await cli.post(
        "/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "bike",
                    "regions": [2],
                    "working_hours": ["12:35-14:00", "09:00-11:00"],
                },
            ]
        },
    )
    json_response = await response.json()
    assert response.status == 400
    assert response.reason == "Bad Request"
    assert json_response["validation_error"]["couriers"] == [{"id": 1}]
    assert json_response["validation_error"]["errors_data"][0]["msg"] == "id duplicates"
