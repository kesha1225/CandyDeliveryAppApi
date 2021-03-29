from typing import Tuple, Dict, List, Union

from aiohttp import web
from aiohttp.web_request import Request
from pydantic import validate_model
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil import parser

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
            web.HTTPOk.status_code,
            web.HTTPOk().reason,
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

        response, reason, data = await cls.get_model_from_json_data(json_data)

        assign_time, orders = await Order.get_orders_for_courier(
            session=session, courier_id=data["courier_id"]
        )
        response_data: Dict[str, Union[List[Dict[str, int]], str]] = {"orders": []}

        for order in orders:
            response_data["orders"].append({"id": order.id})

        if orders:
            response_data["assign_time"] = assign_time

        model = OrdersAssignPostResponseModel(**response_data)

        return ApiResponse(status_code=response,
                           reason=reason,
                           response_data=model)


class OrdersCompletePostRequest(OrdersCompletePostRequestModel):
    @classmethod
    async def get_model_from_json_data(
        cls, json_data: dict
    ) -> Tuple[STATUS_CODE, REASON, dict]:
        values, fields_set, error = validate_model(cls, json_data)
        if error is not None:
            raise web.HTTPBadRequest

        return (
            web.HTTPOk.status_code,
            web.HTTPOk().reason,
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

        _, reason, data = await cls.get_model_from_json_data(json_data)

        order_id, courier_id, complete_time = (
            data["order_id"],
            data["courier_id"],
            data["complete_time"],
        )
        complete_time = parser.isoparse(complete_time)

        order = await Order.get_one(session=session, _id=order_id)
        if (
            order is None
            or (order.courier_id is None and not order.completed)
            or (not order.completed and order.courier_id != courier_id)
            or (order.completed and order.old_courier_id != courier_id)
            or (order.completed and order.completed_time != complete_time.isoformat())
        ):
            raise web.HTTPBadRequest

        await Order.complete_order(
            session=session, order_id=order_id, complete_time=complete_time
        )
        return ApiResponse(
            status_code=web.HTTPOk.status_code,
            reason=web.HTTPOk().reason,
            response_data=OrdersCompletePostResponseModel(**{"order_id": order_id}),
        )
