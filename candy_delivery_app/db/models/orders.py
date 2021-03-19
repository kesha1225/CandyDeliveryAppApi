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

        print(courier.get_capacity())

        orders = await session.execute(
            select(Order).filter(
                and_(
                    Order.region.in_(courier.regions),
                    Order.weight <= courier.get_capacity(),
                )
            )
        )
        for i in orders.fetchall():
            i = i[0]
            print(i.__dict__)
