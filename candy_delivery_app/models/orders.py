import datetime
from typing import List, Union, Optional, Dict, Tuple

from pydantic import Field, conint, confloat, validator, BaseModel
from dateutil import parser

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


class OrdersIdsAP(BaseModel):
    orders: List[OrderId] = Field(..., min_items=1)
    errors_data: List[Dict[str, Union[Tuple, str]]]


class OrdersBadRequestModel(BaseModel):
    validation_error: OrdersIdsAP


class OrdersAssignPostRequestModel(CoreModel):
    courier_id: COURIER_ID


class OrdersAssignPostResponseModel(CoreModel):
    orders: List[OrderId]
    assign_time: Optional[datetime.datetime]


class OrdersCompletePostRequestModel(CoreModel):
    courier_id: COURIER_ID
    order_id: ORDER_ID
    complete_time: str

    @validator("complete_time")
    def check_time_type(cls, value):
        try:
            parser.isoparse(value)
        except ValueError:
            raise ValueError()
        return value


class OrdersCompletePostResponseModel(CoreModel):
    order_id: ORDER_ID
