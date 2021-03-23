import datetime
from typing import List, Union, Optional

from pydantic import Field, conint, confloat, validator

from ._types import COURIER_ID, ORDER_ID, HOURS_LIST
from .settings import CoreModel
from .utils import hours_validate


class OrderItem(CoreModel):
    order_id: ORDER_ID
    weight: Union[confloat(strict=True, gt=0.0), conint(strict=True, gt=0)]
    region: conint(strict=True, gt=0)
    delivery_hours: HOURS_LIST

    _normalize_delivery_hours = validator("delivery_hours", allow_reuse=True)(
        hours_validate
    )


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


class OrdersAssignPostEmptyResponseModel(CoreModel):
    orders: List[OrderId]


class OrdersAssignPostResponseModel(OrdersAssignPostEmptyResponseModel):
    orders: List[OrderId]
    assign_time: Optional[datetime.datetime]


class OrdersCompletePostRequestModel(CoreModel):
    courier_id: COURIER_ID
    order_id: ORDER_ID
    complete_time: datetime.datetime


class OrdersCompletePostResponseModel(CoreModel):
    order_id: ORDER_ID
