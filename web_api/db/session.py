from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from core import get_settings
from sqlmodel.ext.asyncio.session import AsyncSession

engine = AsyncEngine(
    sync_engine=create_engine(
        str(get_settings().db.postgres_dsn),
        echo=get_settings().db.echo,
        future=True,
        pool_size=get_settings().db.pool_size,
    )
)

async_session_maker = sessionmaker(
    bind=engine, class_=AsyncSession, autocommit=False, autoflush=False, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
