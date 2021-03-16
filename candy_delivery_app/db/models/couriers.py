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
        return await cls.base_db_create(session=session, json_data=json_data, id_key="courier_id")

    @classmethod
    async def get_courier(cls, session: AsyncSession, courier_id: int) -> "Courier":
        result = (
            await session.execute(select(Courier).where(Courier.id == courier_id))
        ).first()[0]
        return result

    @classmethod
    async def patch_courier(
        cls, session: AsyncSession, courier_id: int, new_data: dict
    ) -> Row:
        # TODO: пришело "regions": [1,1]

        new_data = {k: v for k, v in new_data.items() if v is not None}
        new_courier = (
            await session.execute(
                update(Courier)
                .where(Courier.id == courier_id)
                .values(new_data)
                .returning(Courier)
            )
        ).first()
        await session.commit()
        return new_courier
