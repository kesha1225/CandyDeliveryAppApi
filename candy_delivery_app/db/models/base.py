from typing import Union, List, Optional, Tuple, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseDbModel:
    @classmethod
    def get_items_list_from_json(cls: T, json_data: dict, id_key: str) -> List[T]:
        couriers = []
        for data in json_data["data"]:
            data["id"] = data.pop(id_key)
            couriers.append(cls(**data))
        return couriers

    @classmethod
    async def find_duplicates(
        cls: T,
        session: AsyncSession,
        elements: List[T],
    ) -> List[int]:
        ids = [element.id for element in elements]
        old_ids = [
            data[0]
            for data in (
                await session.execute(select(cls.id).where(cls.id.in_(ids)))
            ).fetchall()
        ]
        return old_ids

    @classmethod
    async def base_db_create(
        cls: T,
        session: AsyncSession,
        json_data: dict,
        id_key: str,
    ) -> Tuple[Optional[List[Union[T, int]]], Optional[List[int]]]:
        elements = cls.get_items_list_from_json(json_data=json_data, id_key=id_key)
        old_ids = await cls.find_duplicates(
            session=session,
            elements=elements,
        )

        if old_ids:
            return None, old_ids

        session.add_all(elements)
        await session.commit()
        return elements, None
