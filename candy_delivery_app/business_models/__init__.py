import abc
from typing import Tuple, Union, Any, Type, Optional
from aiohttp.web_request import Request

from pydantic import ValidationError, BaseModel

from ..models._types import STATUS_CODE, REASON, MODEL_DATA


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
