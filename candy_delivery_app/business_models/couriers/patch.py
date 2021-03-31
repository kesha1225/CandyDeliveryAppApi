from typing import Tuple, Union, NoReturn

from aiohttp import web
from aiohttp.web_request import Request
from pydantic import ValidationError, validate_model
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ApiResponse
from candy_delivery_app.db.models.couriers import Courier
from candy_delivery_app.models._types import STATUS_CODE, REASON, MODEL_DATA
from candy_delivery_app.models.couriers import (
    CourierUpdateRequestModel,
    CourierUpdateResponseModel,
    CourierIdForQuery,
    CourierUpdateBadRequestModel,
)


class CourierIdRequest(CourierIdForQuery):
    """
    класс для получения айди из урла
    """

    @classmethod
    async def get_model_from_json_data(
        cls, request: Request
    ) -> Union[Tuple[STATUS_CODE, REASON, MODEL_DATA], NoReturn]:
        values, _, error = validate_model(
            cls, {"id": request.match_info.get("courier_id")}
        )

        if error is not None:
            raise web.HTTPBadRequest

        return web.HTTPOk.status_code, web.HTTPOk().reason, cls.success_handler(values)

    @staticmethod
    def success_handler(values):
        return values["id"]


class CouriersUpdateRequest(CourierUpdateRequestModel):
    @classmethod
    async def get_model_from_json_data(
        cls, request: Request
    ) -> Tuple[STATUS_CODE, REASON, MODEL_DATA]:
        json_data = await request.json()

        _, _, data = await CourierIdRequest.get_model_from_json_data(request=request)
        #  400 быть не может так как там рейс

        values, _, error = validate_model(cls, json_data)

        if error is not None:
            return (
                web.HTTPBadRequest.status_code,
                web.HTTPBadRequest().reason,
                cls.error_handler(validation_error=error),
            )

        return (
            web.HTTPOk.status_code,
            web.HTTPOk().reason,
            cls.success_handler({"new_data": values, "courier_id": data}),
        )

    @classmethod
    def error_handler(
        cls,
        validation_error: ValidationError,
    ):
        errors_data = []
        for error in validation_error.errors():
            errors_data.append(
                {
                    "location": error["loc"],
                    "msg": error["msg"],
                    "type": error["type"],
                }
            )
        response_bad_data = {
            "validation_error": {
                "errors_data": errors_data,
            }
        }
        return response_bad_data

    @staticmethod
    def success_handler(values):
        return values

    @classmethod
    async def patch_courier(
        cls, session: AsyncSession, request: Request
    ) -> ApiResponse:
        status_code, reason, data = await cls.get_model_from_json_data(request=request)
        if status_code == web.HTTPBadRequest.status_code:
            return ApiResponse(
                status_code=status_code,
                reason=reason,
                response_data=CourierUpdateBadRequestModel.parse_obj(data),
            )

        new_courier = await Courier.patch_courier(
            session=session, courier_id=data["courier_id"], new_data=data["new_data"]
        )
        if new_courier is None:
            raise web.HTTPNotFound

        return ApiResponse(
            status_code=status_code,
            reason=reason,
            response_data=CourierUpdateResponseModel.parse_obj(
                {
                    "courier_id": new_courier.id,
                    "courier_type": new_courier.courier_type,
                    "regions": new_courier.regions,
                    "working_hours": new_courier.working_hours,
                }
            ),
        )
