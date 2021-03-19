from aiohttp import web
from sqlalchemy import Float, Interval, select, JSON, String
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
                Order.delivery_hours_timedeltas[1]["first_time"].as_integer()
                == courier.working_hours_timedeltas[0]["first_time"]
            )
        )
        # orders = await session.execute("""SELECT orders.id, orders.weight, orders.region, orders.delivery_hours
        #                          FROM orders
        #                          WHERE CAST(((orders.delivery_hours[1]) ->> 'first_time') AS INTEGER) > 0""")
        for i in orders.fetchall():
            i = i[0]
            print(i.delivery_hours, 11, courier.working_hours)
