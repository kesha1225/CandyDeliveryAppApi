from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ApiResponse
from candy_delivery_app.business_models.base.post import (
    BaseBusinessPostModel,
)
from candy_delivery_app.db.models.couriers import Courier
from candy_delivery_app.models.couriers import (
    CouriersPostRequestModel,
    CouriersBadRequestModel,
    CouriersIds,
)


class CouriersPostRequest(CouriersPostRequestModel, BaseBusinessPostModel):
    @classmethod
    async def create_couriers(
        cls, session: AsyncSession, request: Request
    ) -> ApiResponse:
        return await cls.base_creating(
            session=session,
            request=request,
            bad_request_model=CouriersBadRequestModel,
            success_request_model=CouriersIds,
            create_method=Courier.create_couriers,
            items_key="couriers",
            id_key="courier_id",
        )
