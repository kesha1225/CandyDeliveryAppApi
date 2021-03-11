from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..business_models.couriers import (
    CouriersPostRequest,
    CouriersUpdateRequest,
)
from ..db.db import get_session
from ..db.models.couriers import Courier

couriers_router = web.RouteTableDef()


@couriers_router.post("/couriers")
@get_session
async def import_couriers(request: Request, session: AsyncSession):
    # TODO: working_hours validate
    # TODO: а если ниче не пришло)

    status_code, reason, data, = await CouriersPostRequest.create_courier(
        session=session, request=request
    )
    return web.json_response(data=data, status=status_code, reason=reason)


@couriers_router.patch("/couriers/{courier_id}")
@get_session
async def patch_courier(request: Request, session: AsyncSession):
    # TODO: а че если такого айди в базе нет)

    status_code, reason, data = await CouriersUpdateRequest.patch_courier(
        session=session, request=request
    )
    return web.json_response(data=data, status=status_code, reason=reason)
