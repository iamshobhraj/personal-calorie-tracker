"""Deterministic, repeatable database seeds."""

from __future__ import annotations

import asyncio

from src.persistence.seeds.nutrients import seed_nutrients
from src.persistence.seeds.reviewer import seed_reviewer
from src.persistence.session import get_session_factory


async def seed() -> None:
    """Seed catalog data and an optional reviewer in one transaction."""

    async with get_session_factory().begin() as session:
        await seed_nutrients(session)
        await seed_reviewer(session)


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
