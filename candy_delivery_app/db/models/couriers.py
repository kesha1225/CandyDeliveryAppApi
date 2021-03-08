from sqlalchemy import Column, Integer, String, Enum, ARRAY, FLOAT, DECIMAL
from sqlalchemy.exc import IntegrityError
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
    async def create_couriers(cls, session: AsyncSession, json_data: dict):
        # TODO: проверка есть ли уже в базе айдишник
        couriers = []
        for data in json_data["data"]:
            data["id"] = data.pop("courier_id")
            couriers.append(Courier(**data))
        session.add_all(couriers)
        try:
            await session.commit()
        except IntegrityError as e:
            return None
        return couriers
