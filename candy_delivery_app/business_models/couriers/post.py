from typing import Tuple, List

from aiohttp.web_request import Request
from pydantic import ValidationError
from pydantic.main import validate_model
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ABCModel, CouriersResponse
from candy_delivery_app.db.models.couriers import Courier
from candy_delivery_app.models._types import STATUS_CODE, REASON
from candy_delivery_app.models.couriers import (
    CouriersPostRequestModel,
    CourierItem,
    CouriersBadRequestModel,
    CouriersIds,
)


class CouriersPostRequest(ABCModel, CouriersPostRequestModel):
    @classmethod
    async def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[STATUS_CODE, REASON, dict]:
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
    def success_handler(values: List[CourierItem]) -> dict:
        return {"couriers": [{"id": courier.courier_id} for courier in values]}

    @classmethod
    async def create_couriers(
        cls, session: AsyncSession, request: Request
    ) -> CouriersResponse:
        json_data = await request.json()

        status_code, reason, data = await cls.get_model_from_json_data(
            json_data=json_data
        )

        # TODO: чета вот эти две проверки какие то фу
        if status_code == 400:
            return CouriersResponse(
                status_code=status_code,
                reason=reason,
                response_data=CouriersBadRequestModel.parse_obj(data),
            )

        couriers, errors_ids = await Courier.create_couriers(
            session=session, json_data=json_data
        )
        if errors_ids is not None:
            return CouriersResponse(
                status_code=400,
                reason="Bad Request",
                response_data=CouriersBadRequestModel.parse_obj(
                    {
                        "validation_error": {
                            "couriers": [{"id": id_} for id_ in errors_ids]
                        }
                    }
                ),
            )
        return CouriersResponse(
            status_code=status_code,
            reason=reason,
            response_data=CouriersIds.parse_obj(data),
        )
