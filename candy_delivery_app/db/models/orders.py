import datetime

from aiohttp import web
from sqlalchemy import Float, select, JSON, String, and_, ForeignKey, DateTime, update
from typing import Optional, List, Tuple, Union

from sqlalchemy import (
    Column,
    Integer,
    ARRAY,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

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

    courier_id = Column(Integer, ForeignKey('couriers.id'))

    @classmethod
    async def create_orders(
        cls, session: AsyncSession, json_data: dict
    ) -> Tuple[Optional[List[Union["Order", int]]], Optional[List[int]]]:
        return await cls.create(session=session, json_data=json_data, id_key="order_id")

    @classmethod
    async def get_orders_for_courier(
        cls, session: AsyncSession, courier_id: int
    ) -> Tuple[str, List["Order"]]:
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

        good_orders = []

        raw_orders = orders.fetchall()

        assign_time = datetime.datetime.now().isoformat()

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

                    if (
                        courier_first_time <= order_first_time <= courier_second_time
                    ) or (
                        courier_first_time <= order_second_time <= courier_second_time
                    ):
                        if order not in good_orders:
                            order.courier_id = courier.id
                            order.assign_time = assign_time
                            good_orders.append(order)

        if not good_orders:
            return assign_time, []

        session.add_all(good_orders)
        await session.commit()
        return assign_time, good_orders
