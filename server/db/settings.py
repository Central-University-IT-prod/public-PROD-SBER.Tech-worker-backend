from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from server.config import POSTGRESQL_URL

engine = create_async_engine(POSTGRESQL_URL)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore


Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
