from sqlalchemy import Column, Integer, String, ARRAY, Float

from ..db import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    weight = Column(Float)
    regions = Column(ARRAY(Integer))
    delivery_hours = Column(ARRAY(String))
