from sqlalchemy import Float
from typing import Optional, List, Tuple, Union

from sqlalchemy import (
    Column,
    Integer,
    String,
    ARRAY,
)

from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseDbModel
from ..db import Base


class Order(Base, BaseDbModel):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    weight = Column(Float)
    regions = Column(ARRAY(Integer))
    delivery_hours = Column(ARRAY(String))

    @classmethod
    async def create_orders(
            cls, session: AsyncSession, json_data: dict
    ) -> Tuple[Optional[List[Union["Order", int]]], Optional[List[int]]]:
        return await cls.base_db_create(session=session, json_data=json_data, id_key="order_id")
