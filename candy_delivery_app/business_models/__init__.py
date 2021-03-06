from typing import Union

from ..models._types import STATUS_CODE, REASON
from ..models.couriers import (
    CouriersBadRequestModel,
    CouriersIds,
    CourierUpdateResponseModel, CourierGetResponseModel, CourierUpdateBadRequestModel,
)
from ..models.orders import OrdersAssignPostResponseModel, OrdersCompletePostResponseModel, OrdersBadRequestModel, \
    OrdersIds


class ApiResponse:
    def __init__(
        self,
        status_code: STATUS_CODE,
        reason: REASON,
        response_data: Union[
            CouriersIds,
            OrdersIds,
            CouriersBadRequestModel,
            CourierUpdateResponseModel,
            OrdersAssignPostResponseModel,
            OrdersCompletePostResponseModel,
            CourierGetResponseModel,
            CourierUpdateBadRequestModel,
            OrdersBadRequestModel,
        ],
    ):
        self.status_code = status_code
        self.reason = reason
        self.response_data = response_data
