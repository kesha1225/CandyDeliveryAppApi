from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_routedef import RouteDef
from sqlalchemy.ext.asyncio import AsyncSession

from ..business_models.couriers import CouriersPostRequest
from ..db.db import get_session

couriers_router = web.RouteTableDef()


@couriers_router.post("/couriers")
@get_session
async def import_couriers(request: Request, session: AsyncSession):
    status_code, reason, data = CouriersPostRequest.get_model_from_json_data(json_data=await request.json())
    return web.json_response(data=data, status=status_code, reason=reason)

