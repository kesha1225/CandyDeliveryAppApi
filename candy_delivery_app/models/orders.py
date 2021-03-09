from typing import List

from pydantic import BaseModel, Field

from ._types import COURIER_ID, ORDER_ID


class OrdersPostRequestModel(BaseModel):
    order_id: ORDER_ID = Field(..., gt=0)
    weight: float = Field(..., gt=0.0)
    region: int = Field(..., gt=0)
    delivery_hours: List[str] = Field(..., min_items=1)


class OrderId(BaseModel):
    id: int


class OrdersIds(BaseModel):
    orders: List[OrderId] = Field(..., min_items=1)


class OrdersAssignPostRequestModel(BaseModel):
    courier_id: COURIER_ID = Field(..., gt=0)


class OrdersCompletePostRequestModel(BaseModel):
    courier_id: COURIER_ID = Field(..., gt=0)
    order_id: ORDER_ID = Field(..., gt=0)


class OrdersCompletePostResponseModel(BaseModel):
    order_id: ORDER_ID = Field(..., gt=0)
