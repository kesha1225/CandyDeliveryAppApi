from typing import Tuple, List, Type, Union, Callable

from aiohttp.web_request import Request
from pydantic import ValidationError, BaseModel
from pydantic.main import validate_model
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ApiResponse
from candy_delivery_app.db.models.couriers import Courier
from candy_delivery_app.db.models.orders import Order
from candy_delivery_app.models._types import STATUS_CODE, REASON
from candy_delivery_app.models.couriers import CouriersBadRequestModel, CouriersIds
from candy_delivery_app.models.orders import OrdersBadRequestModel, OrdersIds


async def base_get_model_from_json_data(
    cls, json_data: dict
) -> Tuple[STATUS_CODE, REASON, dict]:
    values, fields_set, error = validate_model(cls, json_data)
    if error is not None:
        return 400, "Bad Request", cls.error_handler(json_data, error)

    return 201, "Created", cls.success_handler(values["data"])


def base_error_handler(
    json_data: dict, validation_error: ValidationError, id_key: str, items_key: str
) -> dict:
    bad_data_ids = []

    if json_data["data"]:  # нам могут отправить пустой список
        for error in validation_error.errors():
            element_number = error["loc"][1]
            element_id = json_data["data"][element_number][id_key]

            if element_id not in bad_data_ids:
                bad_data_ids.append(element_id)

    response_bad_data = {
        "validation_error": {
            items_key: [{"id": element_id} for element_id in bad_data_ids]
        }
    }

    return response_bad_data


def base_success_handler(values: List[BaseModel], items_key: str, id_key: str) -> dict:
    return {items_key: [{"id": element.dict()[id_key]} for element in values]}


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
) -> ApiResponse:
    json_data = await request.json()

    status_code, reason, data = await cls.get_model_from_json_data(json_data=json_data)

    if status_code == 400:
        return ApiResponse(
            status_code=status_code,
            reason=reason,
            response_data=bad_request_model.parse_obj(data),
        )

    couriers, errors_ids = await create_method(
        session=session, json_data=json_data
    )
    if errors_ids is not None:
        return ApiResponse(
            status_code=400,
            reason="Bad Request",
            response_data=bad_request_model.parse_obj(
                {"validation_error": {items_key: [{"id": id_} for id_ in errors_ids]}}
            ),
        )
    return ApiResponse(
        status_code=status_code,
        reason=reason,
        response_data=success_request_model.parse_obj(data),
    )
