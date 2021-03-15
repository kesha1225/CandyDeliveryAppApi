from typing import Union, List, Type, Optional, Tuple, TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


if TYPE_CHECKING:
    from candy_delivery_app.db.models.couriers import Courier
    from candy_delivery_app.db.models.orders import Order


def get_items_list_from_json(
    json_data: dict, db_class: Union[Type["Order"], Type["Courier"]], id_key: str
) -> List[Union["Courier", "Courier"]]:
    couriers = []
    for data in json_data["data"]:
        data["id"] = data.pop(id_key)
        couriers.append(db_class(**data))
    return couriers


async def find_duplicates(
    session: AsyncSession,
    elements: List[Union["Courier", "Courier"]],
    db_class: Union[Type["Order"], Type["Courier"]],
) -> List[int]:
    ids = [element.id for element in elements]
    old_ids = [
        data[0]
        for data in (
            await session.execute(select(db_class.id).where(db_class.id.in_(ids)))
        ).fetchall()
    ]
    return old_ids


async def base_db_create(
    session: AsyncSession,
    json_data: dict,
    db_class: Union[Type["Order"], Type["Courier"]],
    id_key: str,
) -> Tuple[Optional[List[Union[Union["Courier", "Order"], int]]], Optional[List[int]]]:
    elements = get_items_list_from_json(
        json_data=json_data, db_class=db_class, id_key=id_key
    )
    old_ids = await find_duplicates(
        session=session, elements=elements, db_class=db_class
    )

    if old_ids:
        return None, old_ids

    session.add_all(elements)
    await session.commit()
    return elements, None
