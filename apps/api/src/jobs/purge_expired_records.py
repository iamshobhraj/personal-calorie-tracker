from datetime import UTC, datetime

from src.persistence.repositories.idempotency import IdempotencyRepository
from src.persistence.session import get_session_factory
from src.persistence.transaction_manager import SqlAlchemyTransactionManager


async def purge_expired_idempotency_records() -> int:
    """Remove only response records whose defined 24-hour replay window has elapsed."""
    async with SqlAlchemyTransactionManager(get_session_factory(), None) as transaction:
        return await IdempotencyRepository(transaction.session).purge_expired(datetime.now(UTC))
