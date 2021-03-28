from enum import Enum
from typing import List, Optional, Dict, Union, Tuple

from pydantic import Field, validator, confloat, conint, BaseModel
from ._types import COURIER_ID, REGIONS, HOURS_LIST
from .settings import CoreModel
from .utils import hours_validate


class CourierType(str, Enum):
    FOOT = "foot"  # 10
    BIKE = "bike"  # 15
    CAR = "car"  # 50


class CourierItem(CoreModel):
    courier_id: COURIER_ID
    courier_type: CourierType
    regions: REGIONS
    working_hours: HOURS_LIST

    _normalize_working_hours = validator("working_hours", allow_reuse=True)(
        hours_validate
    )


class CourierId(CoreModel):
    id: COURIER_ID


class CourierIdForQuery(CoreModel):
    id: conint(ge=0)


class CouriersIds(CoreModel):
    couriers: List[CourierId] = Field(..., min_items=1)


class CouriersPostRequestModel(CoreModel):
    data: List[CourierItem] = Field(..., min_items=1)


class CouriersIdsAP(BaseModel):
    couriers: List[CourierId] = Field(..., min_items=1)
    errors_data: List[Dict[str, Union[Tuple, str]]]


class CouriersBadRequestModel(BaseModel):
    validation_error: CouriersIdsAP


class CourierGetResponseModel(CoreModel):
    courier_id: COURIER_ID
    courier_type: CourierType
    regions: REGIONS
    working_hours: HOURS_LIST
    rating: Optional[confloat(strict=True, ge=0.0)]
    earnings: conint(ge=0)

    _normalize_working_hours = validator("working_hours", allow_reuse=True)(
        hours_validate
    )


class CourierGetResponseModelNoRating(CoreModel):
    courier_id: COURIER_ID
    courier_type: CourierType
    regions: REGIONS
    working_hours: HOURS_LIST
    earnings: conint(ge=0)

    _normalize_working_hours = validator("working_hours", allow_reuse=True)(
        hours_validate
    )


class CourierUpdateRequestModel(CoreModel):
    courier_type: Optional[CourierType] = None
    regions: Optional[REGIONS] = None
    working_hours: Optional[HOURS_LIST] = None

    _normalize_working_hours = validator("working_hours", allow_reuse=True)(
        hours_validate
    )


class CourierUpdateBadRequestModel(CoreModel):
    validation_error: dict


class CourierUpdateResponseModel(CoreModel):
    courier_id: COURIER_ID
    courier_type: CourierType
    regions: REGIONS
    working_hours: HOURS_LIST

    _normalize_working_hours = validator("working_hours", allow_reuse=True)(
        hours_validate
    )
