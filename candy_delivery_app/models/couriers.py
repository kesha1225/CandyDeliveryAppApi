from enum import Enum
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field
from ._types import COURIER_ID, REGIONS, WORKING_HOURS


class CourierType(str, Enum):
    FOOT = "foot"  # 10
    BIKE = "bike"  # 15
    CAR = "car"  # 50


class CourierItem(BaseModel):
    courier_id: COURIER_ID = Field(..., gt=0)
    courier_type: CourierType
    regions: REGIONS = Field(..., min_items=1, gt=0)
    working_hours: WORKING_HOURS = Field(..., min_items=1)


class CourierId(BaseModel):
    id: int = Field(..., gt=0)


class CouriersIds(BaseModel):
    couriers: List[int] = Field(..., min_items=1, gt=0)


class CouriersPostRequestModel(BaseModel):
    data: List[CourierItem] = Field(..., min_items=1)


class CourierGetResponseModel(BaseModel):
    courier_id: COURIER_ID = Field(..., gt=0)
    courier_type: CourierType
    regions: REGIONS = Field(..., min_items=1, gt=0)
    working_hours: WORKING_HOURS = Field(..., min_items=1)
    rating: float = Field(..., ge=0.0)
    earnings: Decimal = Field(..., ge=0)


class CourierUpdateRequestModel(BaseModel):
    courier_type: Optional[CourierType]
    regions: Optional[REGIONS] = Field(None, min_items=1, gt=0)
    working_hours: Optional[WORKING_HOURS] = Field(None, min_items=1)
