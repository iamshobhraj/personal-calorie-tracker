from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import get_settings

engine: AsyncEngine | None = None
AsyncSessionFactory: async_sessionmaker[AsyncSession] | None = None


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    global AsyncSessionFactory, engine
    if AsyncSessionFactory is None:
        settings = get_settings()
        engine = create_async_engine(
            str(settings.database_url),
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
            echo=False,
        )
        AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)
    return AsyncSessionFactory


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Expose the lazily configured factory to transaction-bound application code."""

    return _get_session_factory()


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped database session without committing implicitly."""

    async with _get_session_factory()() as session:
        yield session


async def database_is_ready() -> bool:
    """Return whether PostgreSQL accepts a simple safe readiness query."""

    try:
        session_factory = _get_session_factory()
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
    except (OSError, SQLAlchemyError):
        return False
    return True
