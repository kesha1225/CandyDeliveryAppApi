from aiohttp import web
from sqlalchemy import Float, Interval, select, JSON, String, and_
from typing import Optional, List, Tuple, Union

from sqlalchemy import (
    Column,
    Integer,
    ARRAY,
)

from sqlalchemy.ext.asyncio import AsyncSession

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

    @classmethod
    async def create_orders(
        cls, session: AsyncSession, json_data: dict
    ) -> Tuple[Optional[List[Union["Order", int]]], Optional[List[int]]]:
        return await cls.create(session=session, json_data=json_data, id_key="order_id")

    @classmethod
    async def get_orders_for_courier(
        cls, session: AsyncSession, courier_id: int
    ) -> Tuple[Optional[List[Union["Order", int]]], Optional[List[int]]]:
        courier = await Courier.get_courier(courier_id=courier_id, session=session)
        if courier is None:
            raise web.HTTPBadRequest

        orders = await session.execute(
            select(Order).filter(
                and_(
                    Order.region.in_(courier.regions),
                    Order.weight <= courier.get_capacity(),
                )
            )
        )
        print("courier", courier.working_hours, courier.working_hours_timedeltas)

        good_orders = []

        raw_orders = orders.fetchall()
        print(len(raw_orders))

        for raw_order in raw_orders:
            order = raw_order[0]

            for order_timedelta in order.delivery_hours_timedeltas:
                for courier_timedelta in courier.working_hours_timedeltas:
                    order_first_time, order_second_time = order_timedelta["first_time"], order_timedelta["second_time"]
                    courier_first_time, courier_second_time = courier_timedelta["first_time"], courier_timedelta["second_time"]

                    if (
                            (courier_first_time <= order_first_time <= courier_second_time)
                            or (courier_first_time <= order_second_time <= courier_second_time)
                    ):
                        if order not in good_orders:
                            good_orders.append(order)

        for i in good_orders:
            print(i.delivery_hours)
