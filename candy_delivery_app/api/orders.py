from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.db import get_session

couriers_router = web.RouteTableDef()


@couriers_router.post("/orders")
@get_session
async def create_orders(request: Request, session: AsyncSession):
    response = await CouriersPostRequest.create_couriers(
        session=session, request=request
    )
    return web.json_response(data=response.response_data.json(), status=response.status_code, reason=response.reason)


