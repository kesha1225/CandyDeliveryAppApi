from typing import Tuple, Union, List, Optional

from pydantic import ValidationError, validate_model

from . import ABCModel
from ..models.couriers import CouriersPostRequestModel, CourierItem, CourierId, CourierUpdateRequestModel


class CouriersPostRequest(ABCModel, CouriersPostRequestModel):
    @classmethod
    def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[int, str, Union[dict, CouriersPostRequestModel]]:
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


class CourierIdRequest(ABCModel, CourierId):
    @classmethod
    def get_model_from_json_data(cls, json_data: dict) -> Tuple[int, Optional[int]]:
        values, fields_set, error = validate_model(cls, {"id": json_data.get("courier_id")})

        if error is not None:
            return 400, None

        return 200, values["id"]


class CouriersUpdateRequest(ABCModel, CourierUpdateRequestModel):
    @classmethod
    def get_model_from_json_data(cls, json_data: dict):
        values, fields_set, error = validate_model(cls, json_data)
        print(error)

        if error is not None:
            return 400, "Bad Request", {}

        return 201, "Created", values
