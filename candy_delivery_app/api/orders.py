from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..business_models.orders.post import OrdersPostRequest
from ..db.db import get_session

orders_router = web.RouteTableDef()


@orders_router.post("/orders")
@get_session
async def create_orders(request: Request, session: AsyncSession):
    response = await OrdersPostRequest.create_orders(
        session=session, request=request
    )
    return web.json_response(data=response.response_data.json(), status=response.status_code, reason=response.reason)


