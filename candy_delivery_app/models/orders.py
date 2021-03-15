from typing import List

from pydantic import Field

from ._types import COURIER_ID, ORDER_ID, HOURS_LIST
from .settings import CoreModel


class OrdersPostRequestModel(CoreModel):
    order_id: ORDER_ID = Field(..., gt=0)
    weight: float = Field(..., gt=0.0)
    region: int = Field(..., gt=0)
    delivery_hours: HOURS_LIST


class OrderId(CoreModel):
    id: int


class OrdersIds(CoreModel):
    orders: List[OrderId] = Field(..., min_items=1)


class OrdersAssignPostRequestModel(CoreModel):
    courier_id: COURIER_ID = Field(..., gt=0)


class OrdersCompletePostRequestModel(CoreModel):
    courier_id: COURIER_ID = Field(..., gt=0)
    order_id: ORDER_ID = Field(..., gt=0)


class OrdersCompletePostResponseModel(CoreModel):
    order_id: ORDER_ID = Field(..., gt=0)
