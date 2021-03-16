from typing import List, Union

from pydantic import Field, conint, confloat

from ._types import COURIER_ID, ORDER_ID, HOURS_LIST
from .settings import CoreModel


class OrderItem(CoreModel):
    order_id: ORDER_ID
    weight: Union[confloat(strict=True, gt=0.0), conint(strict=True, gt=0)]
    region: conint(strict=True, gt=0)
    delivery_hours: HOURS_LIST


class OrderId(CoreModel):
    id: ORDER_ID


class OrdersIds(CoreModel):
    orders: List[OrderId] = Field(..., min_items=1)


class OrdersPostRequestModel(CoreModel):
    data: List[OrderItem] = Field(..., min_items=1)


class OrdersBadRequestModel(CoreModel):
    validation_error: OrdersIds


class OrdersAssignPostRequestModel(CoreModel):
    courier_id: COURIER_ID


class OrdersCompletePostRequestModel(CoreModel):
    courier_id: COURIER_ID
    order_id: ORDER_ID


class OrdersCompletePostResponseModel(CoreModel):
    order_id: ORDER_ID
