from typing import Tuple, Union

from pydantic import ValidationError

from . import ABCModel
from ..models.couriers import CouriersPostRequestModel


class CouriersPostRequest(ABCModel, CouriersPostRequestModel):
    @classmethod
    def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[int, str, Union[dict, CouriersPostRequestModel]]:
        try:
            deserialized_model = cls(**json_data)
        except ValidationError as error:
            return 400, "Bad Request", cls.error_handler(json_data, error)

        return 201, "Created", deserialized_model.success_handler()

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

    def success_handler(self):
        return {"couriers": [{"id": courier.courier_id} for courier in self.data]}
