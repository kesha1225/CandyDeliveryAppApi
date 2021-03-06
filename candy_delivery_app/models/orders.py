from typing import List

from pydantic import BaseModel, Field

from ._types import COURIER_ID, ORDER_ID


class OrdersPostRequestModel(BaseModel):
    order_id: ORDER_ID = Field(..., ge=0)
    weight: int = Field(..., ge=0)
    region: int = Field(..., ge=0)
    delivery_hours: List[str] = Field(..., min_items=1)


class OrderId(BaseModel):
    id_: int = Field(..., alias="id", ge=0)


class OrdersIds(BaseModel):
    orders: List[OrderId] = Field(..., min_items=1)


class OrdersAssignPostRequestModel(BaseModel):
    courier_id: COURIER_ID = Field(..., ge=0)


class OrdersCompletePostRequestModel(BaseModel):
    courier_id: COURIER_ID = Field(..., ge=0)
    order_id: ORDER_ID = Field(..., ge=0)


class OrdersCompletePostResponseModel(BaseModel):
    order_id: ORDER_ID = Field(..., ge=0)
