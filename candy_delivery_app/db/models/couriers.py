from typing import Optional, List, Tuple, Union

from sqlalchemy import (
    Column,
    Integer,
    Enum,
    ARRAY,
    FLOAT,
    JSON,
    String,
    select,
)
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload

from .base import BaseDbModel
from ..db import Base
from ...models.couriers import CourierType


class Courier(Base, BaseDbModel):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True)
    courier_type = Column(Enum(CourierType))
    regions = Column(ARRAY(Integer))
    working_hours = Column(ARRAY(String))
    working_hours_timedeltas = Column(ARRAY(JSON))

    orders = relationship("Order", backref="courier")

    rating = Column(FLOAT, nullable=True)
    earnings = Column(Integer, default=0)

    last_delivery_time = Column(FLOAT, nullable=True)
    delivery_data = Column(JSON, nullable=True)

    def get_capacity(self):
        return {
            CourierType.FOOT: 10,
            CourierType.BIKE: 15,
            CourierType.CAR: 50,
        }[self.courier_type]

    def get_coefficient(self):
        return {
            CourierType.FOOT: 2,
            CourierType.BIKE: 5,
            CourierType.CAR: 9,
        }[self.courier_type]

    @classmethod
    async def create_couriers(
        cls, session: AsyncSession, json_data: dict
    ) -> Tuple[Optional[List[Union["Courier", int]]], Optional[List[int]]]:
        return await cls.create(
            session=session, json_data=json_data, id_key="courier_id"
        )

    @classmethod
    async def get_one(cls, session: AsyncSession, _id: int) -> Optional["Courier"]:
        result = (
            await session.execute(
                select(cls).where(cls.id == _id).options(selectinload(cls.orders))
            )
        ).first()
        return result[0] if result is not None else result

    @classmethod
    async def get_courier(
        cls, session: AsyncSession, courier_id: int
    ) -> Optional["Courier"]:
        return await cls.get_one(session=session, _id=courier_id)

    @classmethod
    async def get_all_data_courier(
        cls, session: AsyncSession, courier_id: int
    ) -> Optional["Courier"]:
        base_courier = await cls.get_courier(session=session, courier_id=courier_id)
        if base_courier is None:
            return base_courier

        average_values = []

        if base_courier.delivery_data is None:
            return base_courier

        for region, times in base_courier.delivery_data["regions"].items():
            average_values.append(sum(times) / len(times))

        if not average_values:
            return base_courier

        t = min(average_values)

        rating = (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5
        base_courier.rating = round(rating, 2)
        await session.commit()
        return base_courier

    @classmethod
    async def patch_courier(
        cls, session: AsyncSession, courier_id: int, new_data: dict
    ) -> Row:
        return await cls.patch(session=session, _id=courier_id, new_data=new_data)
