from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from candy_delivery_app.db.context_uri import DB_URI

Base = declarative_base()

engine = create_async_engine(DB_URI.get(), echo=False)

session = sessionmaker(engine, class_=AsyncSession)


def get_session(func):
    async def wrapper(request):
        # await update_base()
        async_session = session(expire_on_commit=False)
        try:
            response = await func(request, async_session)
        finally:
            # print((await async_session.execute("SELECT * FROM couriers")).fetchall())
            # print((await async_session.execute("SELECT * FROM orders")).fetchall())
            await async_session.close()

        return response

    return wrapper


async def update_base():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
