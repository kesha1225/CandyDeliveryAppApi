from sqlalchemy import Column, Integer, String, ARRAY, Float
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

from .base import get_items_list_from_json, find_duplicates
from ..db import Base
from ...models.couriers import CourierType
from ..db import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    weight = Column(Float)
    regions = Column(ARRAY(Integer))
    delivery_hours = Column(ARRAY(String))

    @classmethod
    async def create_orders(
            cls, session: AsyncSession, json_data: dict
    ) -> Tuple[Optional[List[Union["Order", int]]], Optional[List[int]]]:
        orders = get_items_list_from_json(json_data=json_data, db_class=cls, id_key="order_id")
        old_ids = await find_duplicates(session=session, elements=orders, db_class=cls)

        if old_ids:
            return None, old_ids

        session.add_all(orders)
        await session.commit()
        return couriers, None
