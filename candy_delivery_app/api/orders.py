from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..business_models.orders.post import (
    OrdersPostRequest,
    OrdersAssignPostRequest,
    OrdersCompletePostRequest,
)
from ..db.db import get_session
from ..db.models.couriers import Courier
from ..db.models.orders import Order

orders_router = web.RouteTableDef()


@orders_router.post("/orders")
@get_session
async def create_orders(request: Request, session: AsyncSession):
    response = await OrdersPostRequest.create_orders(session=session, request=request)
    return web.json_response(
        data=response.response_data.json(),
        status=response.status_code,
        reason=response.reason,
    )


@orders_router.post("/orders/assign")
@get_session
async def assign_orders(request: Request, session: AsyncSession):
    response = await OrdersAssignPostRequest.assign_orders(
        session=session, request=request
    )

    return web.json_response(
        data=response.response_data.json(),
        status=response.status_code,
        reason=response.reason,
    )


@orders_router.post("/orders/complete")
@get_session
async def complete_orders(request: Request, session: AsyncSession):
    response = await OrdersCompletePostRequest.complete_orders(
        session=session, request=request
    )
    return web.json_response(
        data=response.response_data.json(),
        status=response.status_code,
        reason=response.reason,
    )
