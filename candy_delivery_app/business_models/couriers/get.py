from typing import Tuple

from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ApiResponse
from candy_delivery_app.business_models.couriers.patch import CourierIdRequest
from candy_delivery_app.db.models.couriers import Courier
from candy_delivery_app.models._types import STATUS_CODE, REASON, MODEL_DATA
from candy_delivery_app.models.couriers import (
    CourierGetResponseModel,
)


class CouriersGetRequest(CourierGetResponseModel):
    @classmethod
    async def get_model_from_json_data(
        cls, request: Request
    ) -> Tuple[STATUS_CODE, REASON, MODEL_DATA]:

        _, _, data = await CourierIdRequest.get_model_from_json_data(request=request)

        return (
            web.HTTPOk.status_code,
            web.HTTPOk().reason,
            cls.success_handler(data),
        )

    @staticmethod
    def success_handler(values):
        return values

    @classmethod
    async def get_courier(cls, session: AsyncSession, request: Request) -> ApiResponse:
        status_code, reason, data = await cls.get_model_from_json_data(request=request)
        courier = await Courier.get_all_data_courier(session=session, courier_id=data)
        if courier is None:
            raise web.HTTPNotFound

        response = {
            "courier_id": courier.id,
            "courier_type": courier.courier_type,
            "regions": courier.regions,
            "working_hours": courier.working_hours,
        }

        if courier.delivery_data:
            response["rating"] = courier.rating

        response["earnings"] = courier.earnings

        return ApiResponse(
            status_code=status_code,
            reason=reason,
            response_data=CourierGetResponseModel.parse_obj(response),
        )
