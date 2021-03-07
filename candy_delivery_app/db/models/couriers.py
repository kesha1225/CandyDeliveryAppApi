from sqlalchemy import Column, Integer, String, Enum, ARRAY, FLOAT, DECIMAL

from ..db import Base
from ...models.couriers import CourierType


class Courier(Base):
    __tablename__ = 'couriers'

    id = Column(Integer, primary_key=True)
    courier_type = Column(Enum(CourierType))
    regions = Column(ARRAY(Integer))
    working_hours = Column(ARRAY(String))
    rating = Column(FLOAT)
    earnings = Column(DECIMAL)

    # TODO: отношения с ордерами (интимные)
