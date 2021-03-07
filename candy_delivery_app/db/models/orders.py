from sqlalchemy import Column, Integer, String, ARRAY

from ..db import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    weight = Column(Integer)
    regions = Column(Integer)
    delivery_hours = Column(ARRAY(String))
