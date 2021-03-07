from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# TODO: .env
engine = create_async_engine(
    "postgresql+asyncpg://postgres:samedov@localhost:5432/postgres", echo=True
)

session = sessionmaker(engine, class_=AsyncSession)


def get_session(func):
    async def wrapper(request):
        async_session = session()
        response = await func(request, session)
        await async_session.close()
        return response

    return wrapper


async def update_base():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
