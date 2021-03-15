from typing import Union, List, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from candy_delivery_app.db.models.couriers import Courier
from candy_delivery_app.db.models.orders import Order


def get_items_list_from_json(json_data: dict, db_class: Union[Type[Order], Type[Courier]], id_key: str) -> List[
    Union[Courier, Courier]]:
    couriers = []
    for data in json_data["data"]:
        data["id"] = data.pop(id_key)
        couriers.append(db_class(**data))
    return couriers


async def find_duplicates(
        session: AsyncSession, elements: List[Union[Courier, Courier]], db_class: Union[Type[Order], Type[Courier]],
) -> List[int]:
    ids = [element.id for element in elements]
    old_ids = [
        data[0]
        for data in (
            await session.execute(select(db_class.id).where(db_class.id.in_(ids)))
        ).fetchall()
    ]
    return old_ids
