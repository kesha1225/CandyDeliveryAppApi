from typing import Tuple, List, Type, Union, Callable

from aiohttp import web
from aiohttp.web_request import Request
from pydantic import ValidationError, BaseModel
from pydantic.main import validate_model
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ApiResponse
from candy_delivery_app.models._types import STATUS_CODE, REASON
from candy_delivery_app.models.couriers import CouriersBadRequestModel, CouriersIds
from candy_delivery_app.models.orders import OrdersBadRequestModel, OrdersIds


class BaseBusinessPostModel:
    @classmethod
    async def get_model_from_json_data(
        cls, json_data: dict, id_key: str, items_key: str
    ) -> Tuple[STATUS_CODE, REASON, dict]:
        values, fields_set, error = validate_model(cls, json_data)
        if error is not None:
            return (
                web.HTTPBadRequest.status_code,
                web.HTTPBadRequest().reason,
                cls.error_handler(json_data, error, id_key=id_key, items_key=items_key),
            )

        return (
            web.HTTPCreated.status_code,
            web.HTTPCreated().reason,
            cls.success_handler(values["data"], id_key=id_key, items_key=items_key),
        )

    @classmethod
    def error_handler(
        cls,
        json_data: dict,
        validation_error: ValidationError,
        id_key: str,
        items_key: str,
    ) -> dict:
        bad_data_ids = []

        errors_data = []

        if json_data[
            "data"
        ]:  # нам могут отправить пустой список (вообще не могу, но пусть будет)
            for error in validation_error.errors():
                errors_data.append(
                    {
                        "location": error["loc"],
                        "msg": error["msg"],
                        "type": error["type"],
                    }
                )
                element_number = error["loc"][1]
                element_id = json_data["data"][element_number][id_key]

                if element_id not in bad_data_ids:
                    bad_data_ids.append(element_id)

        response_bad_data = {
            "validation_error": {
                items_key: [{"id": element_id} for element_id in bad_data_ids],
                "errors_data": errors_data,
            }
        }

        return response_bad_data

    @classmethod
    def success_handler(
        cls, values: List[BaseModel], items_key: str, id_key: str
    ) -> dict:
        return {items_key: [{"id": element.dict()[id_key]} for element in values]}

    @classmethod
    async def base_creating(
        cls,
        session: AsyncSession,
        request: Request,
        bad_request_model: Union[
            Type[OrdersBadRequestModel], Type[CouriersBadRequestModel]
        ],
        success_request_model: Union[Type[CouriersIds], Type[OrdersIds]],
        create_method: Callable,
        items_key: str,
        id_key: str,
    ) -> ApiResponse:
        json_data = await request.json()

        status_code, reason, data = await cls.get_model_from_json_data(
            json_data, id_key=id_key, items_key=items_key
        )

        if status_code == web.HTTPBadRequest.status_code:
            return ApiResponse(
                status_code=status_code,
                reason=reason,
                response_data=bad_request_model.parse_obj(data),
            )

        _, errors_ids = await create_method(session=session, json_data=json_data)
        if errors_ids is not None:
            errors_data = []
            for error_id in errors_ids:
                for i, element in enumerate(json_data["data"]):
                    if element["id"] == error_id:
                        errors_data.append(
                            {
                                "location": ("data", i, id_key),
                                "msg": "id duplicates",
                                "type": "IntegrityError",
                            }
                        )

            return ApiResponse(
                status_code=web.HTTPBadRequest.status_code,
                reason=web.HTTPBadRequest().reason,
                response_data=bad_request_model.parse_obj(
                    {
                        "validation_error": {
                            items_key: [{"id": id_} for id_ in errors_ids],
                            "errors_data": errors_data,
                        }
                    }
                ),
            )
        return ApiResponse(
            status_code=status_code,
            reason=reason,
            response_data=success_request_model.parse_obj(data),
        )
