from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class TransactionManager(Protocol):
    async def __aenter__(self) -> Self: ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    @property
    def session(self) -> AsyncSession: ...


class SqlAlchemyTransactionManager:
    """Own a transaction and set tenant context only for that transaction."""

    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession], user_id: UUID | None
    ) -> None:
        self._session_factory = session_factory
        self._user_id = user_id
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Transaction manager has not been entered")
        return self._session

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        await self._session.begin()
        if self._user_id is not None:
            await self._session.execute(
                text("SELECT set_config('app.user_id', :user_id, true)"),
                {"user_id": str(self._user_id)},
            )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()
            self._session = None
