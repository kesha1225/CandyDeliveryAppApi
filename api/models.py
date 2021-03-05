from typing import List
from enum import Enum

from pydantic import BaseModel, Field


REGIONS = List[int]
WORKING_HOURS = List[str]
ORDER_ID = int
COURIER_ID = int


class CourierType(str, Enum):
    FOOT = "foot"
    BIKE = "bike"
    CAR = "car"


class CourierItem(BaseModel):
    courier_id: COURIER_ID
    courier_type: CourierType
    regions: REGIONS
    working_hours: WORKING_HOURS = Field(..., min_items=1)


class CourierId(BaseModel):
    id_: int = Field(..., alias="id")


class CouriersIds(BaseModel):
    couriers: List[CourierId]


class CouriersPostRequest(BaseModel):
    data: List[CourierItem]


class CourierGetResponse(BaseModel):
    courier_id: COURIER_ID
    courier_type: CourierType
    regions: REGIONS
    working_hours: WORKING_HOURS = Field(..., min_items=1)
    rating: int
    earnings: int


class CourierUpdateRequest(BaseModel):
    courier_type: CourierType
    regions: REGIONS
    working_hours: WORKING_HOURS = Field(..., min_items=1)


class OrdersPostRequest(BaseModel):
    order_id: ORDER_ID
    weight: int
    region: int
    delivery_hours: List[str]


class OrderId(BaseModel):
    id_: int = Field(..., alias="id")


class OrdersIds(BaseModel):
    orders: List[OrderId]


class OrdersAssignPostRequest(BaseModel):
    courier_id: COURIER_ID


class OrdersCompletePostRequest(BaseModel):
    courier_id: COURIER_ID
    order_id: ORDER_ID


class OrdersCompletePostResponse(BaseModel):
    order_id: ORDER_ID
