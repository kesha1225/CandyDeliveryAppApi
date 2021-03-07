from sqlalchemy import Column, Integer, String, Enum, ARRAY

from ..db import Base
from ...models.couriers import CourierType


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    weight = Column(Integer)
    regions = Column(Integer)
    delivery_hours = Column(ARRAY(String))
