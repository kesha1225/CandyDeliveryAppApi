from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ApiResponse
from candy_delivery_app.business_models.base.post import BaseBusinessPostModel
from candy_delivery_app.db.models.orders import Order
from candy_delivery_app.models.orders import (
    OrdersPostRequestModel,
    OrdersIds,
    OrdersBadRequestModel,
)


class OrdersPostRequest(OrdersPostRequestModel, BaseBusinessPostModel):
    @classmethod
    async def create_orders(
        cls, session: AsyncSession, request: Request
    ) -> ApiResponse:
        return await cls.base_creating(
            session=session,
            request=request,
            bad_request_model=OrdersBadRequestModel,
            success_request_model=OrdersIds,
            create_method=Order.create_orders,
            items_key="orders",
            id_key="order_id",
        )
