from aiohttp import web
from sqlalchemy import Float, Interval, select
from typing import Optional, List, Tuple, Union

from sqlalchemy import (
    Column,
    Integer,
    String,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import array

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import op

from .base import BaseDbModel
from .couriers import Courier
from ..db import Base


class Order(Base, BaseDbModel):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    weight = Column(Float)
    region = Column(Integer)
    delivery_hours = Column(ARRAY(Interval))

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

        print(courier.working_hours)


        # aaaaaaaaaaaaaaaaaaaaaaa

        orders = await session.execute(select(Order).filter(Order.delivery_hours[0][0] > courier.working_hours[0][0]))
        for i in orders.fetchall():
            i = i[0]
            print(i.delivery_hours[0][0], courier.working_hours[0][0])
