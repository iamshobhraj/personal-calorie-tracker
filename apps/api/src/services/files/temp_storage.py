from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path


@asynccontextmanager
async def temporary_directory(root: Path) -> AsyncIterator[Path]:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    try:
        yield root
    finally:
        for item in root.glob("*.upload"):
            if item.is_file() and item.resolve().parent == root:
                item.unlink(missing_ok=True)
