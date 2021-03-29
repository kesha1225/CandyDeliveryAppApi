import datetime
from typing import Optional, List, Tuple, Union

from aiohttp import web
from sqlalchemy import Column, Integer, ARRAY
from sqlalchemy import (
    Float,
    select,
    JSON,
    String,
    and_,
    ForeignKey,
    update,
    Boolean,
    not_,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.operators import is_

from .base import BaseDbModel
from .couriers import Courier
from .utils import check_courier_can_delivery_by_time
from ..db import Base
from ...business_models.orders.utils import get_best_orders


class Order(Base, BaseDbModel):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    weight = Column(Float)
    region = Column(Integer)
    delivery_hours = Column(ARRAY(String))
    delivery_hours_timedeltas = Column(ARRAY(JSON))
    assign_time = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

    courier_id = Column(Integer, ForeignKey("couriers.id"))
    old_courier_id = Column(Integer, nullable=True)
    cost = Column(Integer)

    completed_time = Column(String, nullable=True)

    @classmethod
    async def create_orders(
        cls, session: AsyncSession, json_data: dict
    ) -> Tuple[Optional[List[Union["Order", int]]], Optional[List[int]]]:
        return await cls.create(session=session, json_data=json_data, id_key="order_id")

    @classmethod
    async def get_one(cls, session: AsyncSession, _id: int) -> Optional["Order"]:
        result = (await session.execute(select(cls).where(cls.id == _id))).first()
        return result[0] if result is not None else result

    @classmethod
    async def get_orders_for_courier(
        cls, session: AsyncSession, courier_id: int
    ) -> Tuple[str, List["Order"]]:

        courier = await Courier.get_courier(courier_id=courier_id, session=session)
        if courier is None:
            raise web.HTTPBadRequest

        if not courier.regions or not courier.working_hours:
            return "", []

        orders = await session.execute(
            select(Order)
            .filter(
                and_(
                    Order.region.in_(courier.regions),
                    not_(Order.completed),
                    Order.weight <= courier.get_capacity(),
                    is_(Order.courier_id, None),
                )
            )
            .order_by(Order.weight)
        )

        good_orders = []
        orders_sum_weight = 0

        if courier.orders:
            return courier.orders[0].assign_time, courier.orders

        raw_orders = get_best_orders(
            [raw_order[0] for raw_order in orders.fetchall()],
            capacity=courier.get_capacity(),
        )

        assign_time = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

        for order in raw_orders:
            for order_timedelta in order.delivery_hours_timedeltas:
                for courier_timedelta in courier.working_hours_timedeltas:
                    if (
                        check_courier_can_delivery_by_time(
                            order_timedelta=order_timedelta,
                            courier_timedelta=courier_timedelta,
                        )
                        and (order not in good_orders)
                        and (
                            round(orders_sum_weight + order.weight, 2)
                            <= courier.get_capacity()
                        )
                    ):
                        orders_sum_weight = round(orders_sum_weight + order.weight, 2)
                        order.cost = 500 * courier.get_coefficient()
                        order.courier_id = courier.id
                        order.assign_time = assign_time
                        good_orders.append(order)

        if not good_orders:
            return assign_time, []

        session.add_all(good_orders)
        await session.commit()
        return assign_time, good_orders

    @classmethod
    async def complete_order(
        cls, session: AsyncSession, order_id: int, complete_time: datetime.datetime
    ) -> None:
        order = (
            await session.execute(
                select(Order)
                .where(Order.id == order_id)
                .options(selectinload(Order.courier))
            )
        ).fetchall()[0][0]
        if order.courier is None:
            return

        courier = (
            await session.execute(
                select(Courier)
                .where(Courier.id == order.courier_id)
                .options(selectinload(Courier.orders))
            )
        ).fetchall()[0][0]
        cid = order.courier_id

        order.courier.earnings += order.cost

        if order.courier.delivery_data is None:
            order.courier.delivery_data = {"regions": {}, "not_completed_regions": {}}

        complete_time_seconds = complete_time.timestamp()
        if order.courier.last_delivery_time is None:
            delivery_time = (
                complete_time_seconds
                - datetime.datetime.fromisoformat(order.assign_time).timestamp()
            )
            order.courier.last_delivery_time = complete_time_seconds
        else:
            delivery_time = complete_time_seconds - order.courier.last_delivery_time
            order.courier.last_delivery_time = complete_time_seconds

        # 1616434714.838184
        region_key = str(order.region)

        if len(courier.orders) > 1:
            if (
                order.courier.delivery_data["not_completed_regions"].get(region_key)
                is None
            ):
                order.courier.delivery_data["not_completed_regions"][region_key] = [
                    delivery_time
                ]
            else:
                order.courier.delivery_data["not_completed_regions"][region_key].append(
                    delivery_time
                )
        else:
            for k, v in order.courier.delivery_data["not_completed_regions"].items():
                if order.courier.delivery_data["regions"].get(k) is None:
                    order.courier.delivery_data["regions"][k] = v
                else:
                    order.courier.delivery_data["regions"][k].extend(v)

            if order.courier.delivery_data["regions"].get(region_key) is None:
                order.courier.delivery_data["regions"][region_key] = [delivery_time]
            else:
                order.courier.delivery_data["regions"][region_key].append(delivery_time)

            order.courier.delivery_data["not_completed_regions"] = {}

        # работай пж
        await session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(
                {
                    "completed": True,
                    "courier_id": None,
                    "old_courier_id": order.courier.id,
                    "completed_time": complete_time.isoformat(),
                }
            )
        )
        await session.execute(
            update(Courier)
            .where(Courier.id == order.courier.id)
            .values({"delivery_data": order.courier.delivery_data})
        )
        await session.commit()
