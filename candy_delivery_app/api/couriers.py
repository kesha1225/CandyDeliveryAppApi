from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..business_models.couriers import (
    CouriersPostRequest,
    CouriersUpdateRequest,
)
from ..business_models.couriers.get import CouriersGetRequest
from ..db.db import get_session

couriers_router = web.RouteTableDef()


@couriers_router.post("/couriers")
@get_session
async def create_couriers(request: Request, session: AsyncSession):

    response = await CouriersPostRequest.create_couriers(
        session=session, request=request
    )
    return web.json_response(
        data=response.response_data.json(),
        status=response.status_code,
        reason=response.reason,
    )


@couriers_router.patch("/couriers/{courier_id}")
@get_session
async def patch_courier(request: Request, session: AsyncSession):
    response = await CouriersUpdateRequest.patch_courier(
        session=session, request=request
    )
    return web.json_response(
        data=response.response_data.json(),
        status=response.status_code,
        reason=response.reason,
    )


@couriers_router.get("/couriers/{courier_id}")
@get_session
async def get_courier(request: Request, session: AsyncSession):

    response = await CouriersGetRequest.get_courier(
        session=session, request=request
    )
    return web.json_response(
        data=response.response_data.json(exclude_none=True),
        status=response.status_code,
        reason=response.reason,
    )
