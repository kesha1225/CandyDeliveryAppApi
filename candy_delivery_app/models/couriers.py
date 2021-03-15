from enum import Enum
from decimal import Decimal
from typing import List, Optional

from pydantic import Field, validator
from ._types import COURIER_ID, REGIONS, HOURS_LIST
from .settings import CoreModel


class CourierType(str, Enum):
    FOOT = "foot"  # 10
    BIKE = "bike"  # 15
    CAR = "car"  # 50


class CourierItem(CoreModel):
    courier_id: COURIER_ID = Field(..., gt=0)
    courier_type: CourierType
    regions: REGIONS = Field(..., min_items=1, gt=0)
    working_hours: HOURS_LIST


class CourierId(CoreModel):
    id: int = Field(..., gt=0)


class CouriersIds(CoreModel):
    couriers: List[CourierId] = Field(..., min_items=1)


class CouriersPostRequestModel(CoreModel):
    data: List[CourierItem] = Field(..., min_items=1)


class CouriersBadRequestModel(CoreModel):
    validation_error: CouriersIds


class CouriersBadRequestEmptyModel(CoreModel):
    pass


class CourierGetResponseModel(CoreModel):
    courier_id: COURIER_ID = Field(..., gt=0)
    courier_type: CourierType
    regions: REGIONS = Field(..., min_items=1, gt=0)
    working_hours: HOURS_LIST
    rating: Optional[float] = Field(None, ge=0.0)
    earnings: Decimal = Field(..., ge=0)


class CourierUpdateRequestModel(CoreModel):
    courier_type: Optional[CourierType]
    regions: Optional[REGIONS] = Field(None, min_items=1, gt=0)
    working_hours: Optional[HOURS_LIST] = None


class CourierUpdateResponseModel(CoreModel):
    courier_id: COURIER_ID = Field(..., gt=0)
    courier_type: CourierType
    regions: REGIONS = Field(..., min_items=1, gt=0)
    working_hours: HOURS_LIST
