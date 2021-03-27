import datetime
from typing import Tuple, List, Dict

from aiohttp import web
from aiohttp.web_request import Request
from pydantic.main import validate_model, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.business_models import ApiResponse
from candy_delivery_app.business_models.base.post import BaseBusinessPostModel
from candy_delivery_app.db.models.orders import Order
from candy_delivery_app.models._types import STATUS_CODE, REASON
from candy_delivery_app.models.orders import (
    OrdersPostRequestModel,
    OrdersIds,
    OrdersBadRequestModel,
    OrdersAssignPostRequestModel,
    OrdersAssignPostResponseModel,
    OrdersAssignPostEmptyResponseModel,
    OrdersCompletePostRequestModel,
    OrdersCompletePostResponseModel,
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


class OrdersAssignPostRequest(OrdersAssignPostRequestModel):
    @classmethod
    async def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[STATUS_CODE, REASON, dict]:
        values, fields_set, error = validate_model(cls, json_data)
        if error is not None:
            raise web.HTTPBadRequest

        return (
            200,
            "OK",
            cls.success_handler(values),
        )

    @classmethod
    def success_handler(cls, values: Dict[str, int]) -> Dict[str, int]:
        return values

    @classmethod
    async def assign_orders(
        cls, session: AsyncSession, request: Request
    ) -> ApiResponse:
        json_data = await request.json()

        status_code, reason, data = await cls.get_model_from_json_data(json_data)

        assign_time, orders = await Order.get_orders_for_courier(
            session=session, courier_id=data["courier_id"]
        )
        response_data = {"orders": []}

        for order in orders:
            response_data["orders"].append({"id": order.id})

        if orders:
            response_data["assign_time"] = assign_time
            model = OrdersAssignPostResponseModel(**response_data)
        else:
            model = OrdersAssignPostEmptyResponseModel(**response_data)

        return ApiResponse(status_code=200, reason="OK", response_data=model)


class OrdersCompletePostRequest(OrdersCompletePostRequestModel):
    @classmethod
    async def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[STATUS_CODE, REASON, dict]:
        values, fields_set, error = validate_model(cls, json_data)
        if error is not None:
            raise web.HTTPBadRequest

        return (
            200,
            "OK",
            cls.success_handler(values),
        )

    @classmethod
    def success_handler(cls, values: Dict[str, int]) -> Dict[str, int]:
        return values

    @classmethod
    async def complete_orders(
        cls, session: AsyncSession, request: Request
    ) -> ApiResponse:
        json_data = await request.json()

        status_code, reason, data = await cls.get_model_from_json_data(json_data)

        order_id, courier_id, complete_time = (
            data["order_id"],
            data["courier_id"],
            data["complete_time"],
        )

        order = await Order.get_one(session=session, _id=order_id)
        if (
            order is None
            or (order.courier_id is None and not order.completed)
            or (not order.completed and order.courier_id != courier_id)
        ):
            raise web.HTTPBadRequest

        await Order.complete_order(session=session, order_id=order_id, complete_time=complete_time)
        return ApiResponse(
            status_code=200,
            reason="OK",
            response_data=OrdersCompletePostResponseModel(**{"order_id": order_id}),
        )
