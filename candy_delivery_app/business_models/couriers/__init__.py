from typing import Union

from candy_delivery_app.business_models.couriers.patch import CouriersUpdateRequest
from candy_delivery_app.business_models.couriers.post import CouriersPostRequest
from candy_delivery_app.models._types import STATUS_CODE, REASON
from candy_delivery_app.models.couriers import CouriersIds, CouriersBadRequestModel


class CouriersResponse:
    def __init__(
        self,
        status_code: STATUS_CODE,
        reason: REASON,
        response_data: Union[CouriersIds, CouriersBadRequestModel, dict],
    ):
        self.status_code = status_code
        self.reason = reason
        self.response_data = response_data


__all__ = (CouriersPostRequest, CouriersUpdateRequest)
