import abc
from typing import Tuple, Union

from pydantic import ValidationError

from ..models.couriers import CouriersPostRequestModel


class ABCModel(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[int, str, Union[dict, CouriersPostRequestModel]]:
        ...

    @staticmethod
    def error_handler(json_data: dict, validation_error: ValidationError) -> dict:
        ...

    def success_handler(self):
        ...
