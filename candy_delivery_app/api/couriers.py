from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..business_models.couriers import (
    CouriersPostRequest,
    CourierIdRequest,
    CouriersUpdateRequest,
)
from ..db.db import get_session, update_base
from ..db.models.couriers import Courier

couriers_router = web.RouteTableDef()


@couriers_router.post("/couriers")
@get_session
async def import_couriers(request: Request, session: AsyncSession):
    # TODO: working_hours validate
    # TODO: а если ниче не пришло)
    json_data = await request.json()

    status_code, reason, data = CouriersPostRequest.get_model_from_json_data(
        json_data=json_data
    )
    if status_code == 400:  # validation error
        return web.json_response(data=data, status=status_code, reason=reason)

    couriers, errors_ids = await Courier.create_couriers(
        session=session, json_data=json_data
    )
    if errors_ids is not None:  # IntegrityError
        return web.json_response(
            data={"integrity_error": {"couriers": [{"id": id_} for id_ in errors_ids]}},
            status=409,
            reason="Id Dublicates",
        )
    return web.json_response(data=data, status=status_code, reason=reason)


@couriers_router.patch("/couriers/{courier_id}")
@get_session
async def patch_courier(request: Request, session: AsyncSession):
    # TODO: а че если такого айди в базе нет)
    status_code, courier_id = CourierIdRequest.get_model_from_json_data(
        json_data=request.match_info
    )
    if status_code == 400:
        return web.json_response(
            data={"request_error": "courier_id invalid or not set"},
            status=status_code,
            reason="Invalid Data",
        )

    json_data = await request.json()
    status_code, reason, data = CouriersUpdateRequest.get_model_from_json_data(
        json_data=json_data
    )
    if status_code == 400:
        return web.json_response(
            data=data,
            status=status_code,
            reason="Bad Request",
        )

    new_courier = await Courier.patch_courier(
        session=session, courier_id=courier_id, new_data=data
    )
    return web.json_response(
        data={
            "courier_id": new_courier.id,
            "courier_type": new_courier.courier_type,
            "regions": new_courier.regions,
            "working_hours": new_courier.working_hours,
        },
        status=200,
        reason="OK",
    )
