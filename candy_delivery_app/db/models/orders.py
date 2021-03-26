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

from .base import BaseDbModel
from .couriers import Courier
from ..db import Base


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
    cost = Column(Integer)

    # completed_time = Column(Integer, nullable=True)

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

        # выдача новых если например один старый остался и место освободилось

        courier = await Courier.get_courier(courier_id=courier_id, session=session)
        if courier is None:
            raise web.HTTPBadRequest

        orders = await session.execute(
            select(Order).filter(
                and_(Order.region.in_(courier.regions), not_(Order.completed))
            )
        )

        good_orders = []
        orders_sum_weight = 0

        if courier.orders:
            for order in courier.orders:
                good_orders.append(order)
                orders_sum_weight = round(orders_sum_weight + order.weight, 2)

        raw_orders = orders.fetchall()

        assign_time = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

        for raw_order in raw_orders:
            order = raw_order[0]

            for order_timedelta in order.delivery_hours_timedeltas:
                for courier_timedelta in courier.working_hours_timedeltas:
                    order_first_time, order_second_time = (
                        order_timedelta["first_time"],
                        order_timedelta["second_time"],
                    )
                    courier_first_time, courier_second_time = (
                        courier_timedelta["first_time"],
                        courier_timedelta["second_time"],
                    )

                    # if (
                    #     courier_first_time <= order_first_time < courier_second_time
                    #     or courier_first_time < order_second_time <= courier_second_time
                    # ):
                    if (
                        order_first_time < courier_first_time < order_second_time
                        or order_first_time < courier_second_time < order_second_time
                    ) or (
                        courier_first_time < order_first_time < courier_second_time
                        or courier_first_time < order_second_time < courier_second_time
                    ):
                        if (
                            order not in good_orders
                            and orders_sum_weight + order.weight
                            <= courier.get_capacity()
                        ):
                            if (
                                order.courier_id is not None
                            ):  # заказ выдан кому то другому
                                continue
                            orders_sum_weight = round(
                                orders_sum_weight + order.weight, 2
                            )
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
        order.courier.earnings += order.cost

        if order.courier.delivery_data is None:
            order.courier.delivery_data = {"regions": {}}

        complete_time_seconds = complete_time.timestamp()
        if order.courier.last_delivery_time is None:
            delivery_time = (
                complete_time_seconds
                - datetime.datetime.fromisoformat(order.assign_time).timestamp()
            )
            order.courier.last_delivery_time = complete_time_seconds
        else:
            delivery_time = complete_time_seconds - order.courier.last_delivery_time

        # 1616434714.838184
        region_key = str(order.region)

        if order.courier.delivery_data["regions"].get(region_key) is None:
            order.courier.delivery_data["regions"][region_key] = [delivery_time]
        else:
            order.courier.delivery_data["regions"][region_key].append(delivery_time)

        # работай пж
        await session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values({"completed": True, "courier_id": None})
        )
        await session.execute(
            update(Courier)
            .where(Courier.id == order.courier.id)
            .values({"delivery_data": order.courier.delivery_data})
        )
        await session.commit()
