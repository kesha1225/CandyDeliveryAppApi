import abc
from typing import Tuple, Union
from aiohttp.web_request import Request

from pydantic import ValidationError

from ..models._types import STATUS_CODE, REASON, MODEL_DATA
from ..models.couriers import (
    CouriersBadRequestModel,
    CouriersIds,
    CourierUpdateResponseModel,
    CouriersBadRequestEmptyModel,
)


class ApiResponse:
    def __init__(
        self,
        status_code: STATUS_CODE,
        reason: REASON,
        response_data: Union[
            CouriersIds,
            CouriersBadRequestModel,
            dict,
            CourierUpdateResponseModel,
            CouriersBadRequestEmptyModel,
        ],
    ):
        self.status_code = status_code
        self.reason = reason
        self.response_data = response_data


class ABCModel(abc.ABC):
    # TODO: типы
    @classmethod
    @abc.abstractmethod
    async def get_model_from_json_data(
        cls, request_or_json_data: Union[Request, dict]
    ) -> Tuple[STATUS_CODE, REASON, MODEL_DATA]:
        ...

    @staticmethod
    @abc.abstractmethod
    def error_handler(json_data: dict, validation_error: ValidationError) -> dict:
        ...

    @staticmethod
    @abc.abstractmethod
    def success_handler(values):
        ...
