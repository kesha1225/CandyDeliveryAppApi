from typing import Union, List, Optional, Tuple, TypeVar, ClassVar

from sqlalchemy import select, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from candy_delivery_app.models.utils import get_timedeltas_from_string

T = TypeVar("T")


class BaseDbModel:
    @classmethod
    def get_items_list_from_json(cls: T, json_data: dict, id_key: str) -> List[T]:
        items = []
        # TODO: бяка
        for data in json_data["data"]:
            data["id"] = data.pop(id_key)
            if data.get("working_hours"):
                dates = get_timedeltas_from_string(data["working_hours"])
                data["working_hours_timedeltas"] = dates
            elif data.get("delivery_hours"):
                dates = get_timedeltas_from_string(data["delivery_hours"])
                data["delivery_hours_timedeltas"] = dates
            items.append(cls(**data))
        return items

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
    async def create(
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

    @classmethod
    async def get_one(cls: T, session: AsyncSession, _id: int) -> Optional[T]:
        result = (await session.execute(select(cls).where(cls.id == _id).options(selectinload(cls.orders)))).first()
        return result[0] if result is not None else result

    @classmethod
    async def patch(cls: T, session: AsyncSession, _id: int, new_data: dict) -> Row:
        update_data = {}

        for key, value in new_data.items():
            if value is None:
                continue
            if key == "working_hours":
                update_data["working_hours_timedeltas"] = get_timedeltas_from_string(
                    value
                )
            elif key == "delivery_hours":
                update_data["delivery_hours_timedeltas"] = get_timedeltas_from_string(
                    value
                )

            update_data[key] = value

        new_object = (
            await session.execute(
                update(cls).where(cls.id == _id).values(update_data).returning(cls)
            )
        ).first()
        await session.commit()
        return new_object
