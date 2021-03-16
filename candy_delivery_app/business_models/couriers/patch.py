from typing import Tuple

from aiohttp.web_request import Request
from pydantic.main import validate_model
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ABCModel, ApiResponse
from candy_delivery_app.db.models.couriers import Courier
from candy_delivery_app.models._types import STATUS_CODE, REASON, MODEL_DATA
from candy_delivery_app.models.couriers import (
    CourierUpdateRequestModel,
    CouriersBadRequestEmptyModel,
    CourierUpdateResponseModel,
    CourierIdForQuery,
)


class CourierIdRequest(ABCModel, CourierIdForQuery):
    """
    класс для получения айди из урла
    """

    @classmethod
    async def get_model_from_json_data(
        cls, request: Request
    ) -> Tuple[STATUS_CODE, REASON, MODEL_DATA]:
        values, fields_set, error = validate_model(
            cls, {"id": request.match_info.get("courier_id")}
        )

        if error is not None:
            return 400, "Bad Request", cls.error_handler()

        return 200, "OK", cls.success_handler(values)

    @staticmethod
    def error_handler() -> dict:
        """
        В случае, если передано неописанное поле — вернуть HTTP 400 Bad Request.
        """
        return {}

    @staticmethod
    def success_handler(values):
        return values["id"]


class CouriersUpdateRequest(ABCModel, CourierUpdateRequestModel):
    @classmethod
    async def get_model_from_json_data(
        cls, request: Request
    ) -> Tuple[STATUS_CODE, REASON, MODEL_DATA]:
        json_data = await request.json()

        status_code, reason, data = await CourierIdRequest.get_model_from_json_data(
            request=request
        )
        if status_code == 400:
            return status_code, reason, data

        values, fields_set, error = validate_model(cls, json_data)

        if error is not None:
            return 400, "Bad Request", cls.error_handler()

        return (
            200,
            "OK",
            cls.success_handler({"new_data": values, "courier_id": data}),
        )

    @staticmethod
    def error_handler() -> dict:
        return {}

    @staticmethod
    def success_handler(values):
        return values

    @classmethod
    async def patch_courier(
        cls, session: AsyncSession, request: Request
    ) -> ApiResponse:
        status_code, reason, data = await cls.get_model_from_json_data(request=request)
        if status_code == 400:
            return ApiResponse(
                status_code=status_code,
                reason=reason,
                response_data=CouriersBadRequestEmptyModel.parse_obj(data),
            )

        new_courier = await Courier.patch_courier(
            session=session, courier_id=data["courier_id"], new_data=data["new_data"]
        )
        if new_courier is None:
            return ApiResponse(
                status_code=400,
                reason="Bad Request",
                response_data=CouriersBadRequestEmptyModel.parse_obj({}),
            )

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
