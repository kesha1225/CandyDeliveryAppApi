from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from candy_delivery_app.db.context_uri import DB_URI

Base = declarative_base()

engine = create_async_engine(DB_URI.get(), echo=False)

session = sessionmaker(engine, class_=AsyncSession)


def get_session(func):
    async def wrapper(request):
        async_session = session(expire_on_commit=False)
        try:
            response = await func(request, async_session)
        finally:
            await async_session.close()

        return response

    return wrapper


async def update_base():
    async_session = session(expire_on_commit=False)

    await async_session.execute("DROP TABLE IF EXISTS orders CASCADE")
    await async_session.execute("DROP TABLE IF EXISTS couriers CASCADE")
    await async_session.commit()

    await async_session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
