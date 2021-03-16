from typing import Optional, List, Tuple, Union

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ARRAY,
    FLOAT,
    DECIMAL,
    select,
    update,
)
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseDbModel
from ..db import Base
from ...models.couriers import CourierType


class Courier(Base, BaseDbModel):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True)
    courier_type = Column(Enum(CourierType))
    regions = Column(ARRAY(Integer))
    working_hours = Column(ARRAY(String))
    rating = Column(FLOAT, nullable=True)
    earnings = Column(DECIMAL, nullable=True)

    # TODO: отношения с ордерами (интимные)

    @classmethod
    async def create_couriers(
        cls, session: AsyncSession, json_data: dict
    ) -> Tuple[Optional[List[Union["Courier", int]]], Optional[List[int]]]:
        return await cls.create(
            session=session, json_data=json_data, id_key="courier_id"
        )

    @classmethod
    async def get_courier(cls, session: AsyncSession, courier_id: int) -> "Courier":
        return await cls.get_one(session=session, _id=courier_id)

    @classmethod
    async def patch_courier(
        cls, session: AsyncSession, courier_id: int, new_data: dict
    ) -> Row:
        # TODO: пришело "regions": [1,1]
        return await cls.patch(session=session, _id=courier_id, new_data=new_data)
