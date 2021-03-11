from typing import Tuple, Union, List, Optional
from aiohttp.web_request import Request

from pydantic import ValidationError, validate_model
from sqlalchemy.ext.asyncio import AsyncSession

from . import ABCModel
from ..db.models.couriers import Courier
from ..models.couriers import (
    CouriersPostRequestModel,
    CourierItem,
    CourierId,
    CourierUpdateRequestModel,
)
from ..models._types import STATUS_CODE, REASON, MODEL_DATA


class CouriersPostRequest(ABCModel, CouriersPostRequestModel):
    @classmethod
    async def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[STATUS_CODE, REASON, MODEL_DATA]:
        values, fields_set, error = validate_model(cls, json_data)
        if error is not None:
            return 400, "Bad Request", cls.error_handler(json_data, error)

        return 201, "Created", cls.success_handler(values["data"])

    @staticmethod
    def error_handler(json_data: dict, validation_error: ValidationError) -> dict:
        bad_data_ids = []

        if json_data["data"]:  # нам могут отправить пустой список
            for error in validation_error.errors():
                element_number = error["loc"][1]
                courier_id = json_data["data"][element_number]["courier_id"]

                if courier_id not in bad_data_ids:
                    bad_data_ids.append(courier_id)

        response_bad_data = {
            "validation_error": {
                "couriers": [{"id": courier_id} for courier_id in bad_data_ids]
            }
        }

        return response_bad_data

    @staticmethod
    def success_handler(values: List[CourierItem]):
        return {"couriers": [{"id": courier.courier_id} for courier in values]}

    @classmethod
    async def create_courier(
            cls, session: AsyncSession, request: Request
    ) -> Tuple[STATUS_CODE, REASON, MODEL_DATA]:
        json_data = await request.json()

        status_code, reason, data = await cls.get_model_from_json_data(
            json_data=json_data
        )
        if status_code == 400:  # validation error
            return status_code, reason, data

        couriers, errors_ids = await Courier.create_couriers(
            session=session, json_data=json_data
        )
        if errors_ids is not None:  # IntegrityError
            return 409, "Id Dublicates", {"integrity_error": {"couriers": [{"id": id_} for id_ in errors_ids]}}
        return status_code, reason, data


class CourierIdRequest(ABCModel, CourierId):
    @classmethod
    async def get_model_from_json_data(
        cls, request: Request
    ) -> Tuple[STATUS_CODE, REASON, MODEL_DATA]:
        values, fields_set, error = validate_model(
            cls, {"id": request.match_info.get("courier_id")}
        )

        if error is not None:
            return 400, "Invalid Data", cls.error_handler(..., ...)

        return 200, "OK", cls.success_handler(values)

    @staticmethod
    def error_handler(json_data: dict, validation_error: ValidationError) -> dict:
        return {"request_error": "courier_id invalid or not set"}

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
        # id в запросе не угодил нам
        if status_code == 400:
            return status_code, reason, data

        values, fields_set, error = validate_model(cls, json_data)

        if error is not None:
            return 400, "Bad Request", cls.error_handler(..., ...)

        return (
            201,
            "Created",
            cls.success_handler({"new_data": values, "courier_id": data}),
        )

    @staticmethod
    def error_handler(json_data: dict, validation_error: ValidationError) -> dict:
        return {}

    @staticmethod
    def success_handler(values):
        return values

    @classmethod
    async def patch_courier(
        cls, session: AsyncSession, request: Request
    ) -> Tuple[STATUS_CODE, REASON, MODEL_DATA]:
        status_code, reason, data = await cls.get_model_from_json_data(request=request)
        if status_code == 400:
            return status_code, reason, data

        new_courier = await Courier.patch_courier(
            session=session, courier_id=data["courier_id"], new_data=data["new_data"]
        )
        return (
            200,
            "OK",
            {
                "courier_id": new_courier.id,
                "courier_type": new_courier.courier_type,
                "regions": new_courier.regions,
                "working_hours": new_courier.working_hours,
            },
        )
