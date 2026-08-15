from sqlalchemy.ext.asyncio import AsyncSession


class ReportRepository:
    """Reserved for database-level report optimisations; services retain tenant filtering."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
