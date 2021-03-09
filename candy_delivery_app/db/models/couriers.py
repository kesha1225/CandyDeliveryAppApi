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
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import Base
from ...models.couriers import CourierType


class Courier(Base):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True)
    courier_type = Column(Enum(CourierType))
    regions = Column(ARRAY(Integer))
    working_hours = Column(ARRAY(String))
    rating = Column(FLOAT)
    earnings = Column(DECIMAL)

    # TODO: отношения с ордерами (интимные)

    @classmethod
    async def create_couriers(
        cls, session: AsyncSession, json_data: dict
    ) -> Tuple[Optional[List[Union["Courier", int]]], Optional[List[int]]]:
        # TODO: проверка есть ли уже в базе айдишник
        couriers = []
        for data in json_data["data"]:
            data["id"] = data.pop("courier_id")
            couriers.append(Courier(**data))

        ids = [courier.id for courier in couriers]
        old_ids = [
            data[0]
            for data in (
                await session.execute(select(Courier.id).where(Courier.id.in_(ids)))
            ).fetchall()
        ]
        if old_ids:
            return None, old_ids

        session.add_all(couriers)
        await session.commit()
        return couriers, None

    @classmethod
    async def get_courier(cls, session: AsyncSession, courier_id: int) -> "Courier":
        result = (
            await session.execute(select(Courier).where(Courier.id == courier_id))
        ).first()[0]
        return result

    @classmethod
    async def patch_courier(
        cls, session: AsyncSession, courier_id: int, new_data: dict
    ) -> "Courier":
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
