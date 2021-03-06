import abc
from typing import List, Optional, Union, Tuple
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, validator

from api.utils import check_is_regions_positive

REGIONS = List[int]
WORKING_HOURS = List[str]
ORDER_ID = int
COURIER_ID = int


class CourierType(str, Enum):
    FOOT = "foot"  # 10
    BIKE = "bike"  # 15
    CAR = "car"  # 50


class ABCRequestModel(abc.ABC, BaseModel):
    @staticmethod
    @abc.abstractmethod
    def error_handler(json_data: dict, validation_error: ValidationError):
        ...

    @abc.abstractmethod
    def success_handler(self):
        ...


class CourierItem(BaseModel):
    courier_id: COURIER_ID = Field(..., ge=0)
    courier_type: CourierType
    regions: REGIONS = Field(..., min_items=1)
    working_hours: WORKING_HOURS = Field(..., min_items=1)

    @validator("regions")
    def positive_check(cls, value: List[int]):
        check_is_regions_positive(value)


class CourierId(BaseModel):
    id: int


class CouriersIds(BaseModel):
    couriers: List[CourierId]


class CouriersPostRequest(ABCRequestModel, BaseModel):
    data: List[CourierItem] = Field(..., min_items=1)

    @classmethod
    def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[int, str, Union[dict, ABCRequestModel]]:
        try:
            deserialized_model = cls(**json_data)
        except ValidationError as error:
            return 400, "Bad Request", cls.error_handler(json_data, error)

        return 201, "Created", deserialized_model.success_handler()

    @staticmethod
    def error_handler(json_data: dict, validation_error: ValidationError) -> dict:
        bad_data_ids = []

        if json_data["data"]:
            for error in validation_error.errors():
                element_number = error["loc"][1]
                courier_id = json_data["data"][element_number]["courier_id"]

                if courier_id not in bad_data_ids:
                    bad_data_ids.append(courier_id)

        response_bad_data = {
            "validation_error": CouriersIds(
                **{"couriers": [{"id": courier_id} for courier_id in bad_data_ids]}
            ).dict()
        }

        return response_bad_data

    def success_handler(self):
        return CouriersIds(
            **{"couriers": [{"id": courier.courier_id} for courier in self.data]}
        ).dict()


class CourierGetResponse(ABCRequestModel, BaseModel):
    courier_id: COURIER_ID = Field(..., ge=0)
    courier_type: CourierType
    regions: REGIONS = Field(..., min_items=1)
    working_hours: WORKING_HOURS = Field(..., min_items=1)
    rating: float = Field(..., ge=0.0)
    earnings: int = Field(..., ge=0)

    @validator("regions")
    def positive_check(cls, value: List[int]):
        check_is_regions_positive(value)


class CourierUpdateRequest(ABCRequestModel, BaseModel):
    courier_type: Optional[CourierType]
    regions: Optional[REGIONS] = Field(None, min_items=1)
    working_hours: Optional[WORKING_HOURS] = Field(None, min_items=1)

    @validator("regions")
    def positive_check(cls, value: List[int]):
        check_is_regions_positive(value)


class OrdersPostRequest(ABCRequestModel, BaseModel):
    order_id: ORDER_ID = Field(..., ge=0)
    weight: int = Field(..., ge=0)
    region: int = Field(..., ge=0)
    delivery_hours: List[str] = Field(..., min_items=1)


class OrderId(BaseModel):
    id_: int = Field(..., alias="id", ge=0)


class OrdersIds(BaseModel):
    orders: List[OrderId] = Field(..., min_items=1)


class OrdersAssignPostRequest(ABCRequestModel, BaseModel):
    courier_id: COURIER_ID = Field(..., ge=0)


class OrdersCompletePostRequest(ABCRequestModel, BaseModel):
    courier_id: COURIER_ID = Field(..., ge=0)
    order_id: ORDER_ID = Field(..., ge=0)


class OrdersCompletePostResponse(ABCRequestModel, BaseModel):
    order_id: ORDER_ID = Field(..., ge=0)
