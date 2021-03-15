from typing import Tuple, List

from aiohttp.web_request import Request
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ABCModel, ApiResponse
from candy_delivery_app.business_models.base.post import (
    base_get_model_from_json_data,
    base_error_handler,
    base_success_handler,
    base_creating,
)
from candy_delivery_app.db.models.orders import Order
from candy_delivery_app.models._types import STATUS_CODE, REASON
from candy_delivery_app.models.couriers import CourierItem
from candy_delivery_app.models.orders import (
    OrdersPostRequestModel,
    OrdersIds,
    OrdersBadRequestModel,
)


class OrdersPostRequest(ABCModel, OrdersPostRequestModel):
    @classmethod
    async def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[STATUS_CODE, REASON, dict]:
        return await base_get_model_from_json_data(cls, json_data)

    @staticmethod
    def error_handler(json_data: dict, validation_error: ValidationError) -> dict:
        return base_error_handler(
            json_data, validation_error, items_key="orders", id_key="order_id"
        )

    @staticmethod
    def success_handler(values: List[CourierItem]) -> dict:
        return base_success_handler(
            values=values, items_key="orders", id_key="order_id"
        )

    @classmethod
    async def create_orders(
        cls, session: AsyncSession, request: Request
    ) -> ApiResponse:
        return base_creating(
            cls,
            session=session,
            request=request,
            bad_request_model=OrdersBadRequestModel,
            success_request_model=OrdersIds,
            create_method=Order.create_orders,
            items_key="orders",
        )
