from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..business_models.orders.post import OrdersPostRequest, OrdersAssignPostRequest
from ..db.db import get_session
from ..db.models.couriers import Courier
from ..db.models.orders import Order

orders_router = web.RouteTableDef()


@orders_router.post("/orders")
@get_session
async def create_orders(request: Request, session: AsyncSession):
    response = await OrdersPostRequest.create_orders(
        session=session, request=request
    )
    return web.json_response(data=response.response_data.json(), status=response.status_code, reason=response.reason)


@orders_router.post("/orders/assign")
@get_session
async def assign_orders(request: Request, session: AsyncSession):
    response = await OrdersAssignPostRequest.assign_orders(session=session, request=request)

    a = web.json_response(data=response.response_data.json(), status=response.status_code, reason=response.reason)
    # r = await session.execute(select(Courier).options(selectinload(Courier.orders)))
    #
    # for i in r.fetchall():
    #     for j in i[0].orders:
    #         print(j.weight, j.delivery_hours)
    return a


@orders_router.post("/orders/complete")
@get_session
async def complete_orders(request: Request, session: AsyncSession):
    pass
