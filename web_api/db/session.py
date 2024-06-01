from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine

from core import get_settings

engine = AsyncEngine(
    sync_engine=create_engine(
        str(get_settings().db.postgres_dsn),
        echo=get_settings().db.echo,
        future=True,
        pool_size=get_settings().db.pool_size,
    )
)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, autocommit=False, autoflush=False, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
