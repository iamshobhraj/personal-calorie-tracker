from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.enums import UploadStatus
from src.persistence.models.upload import UploadObject


def _safe_temp_directory(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    forbidden = {Path(resolved.anchor), Path.home().resolve(), Path.cwd().resolve()}
    if resolved in forbidden or len(resolved.parts) < 3:
        raise ValueError("Refusing an unsafe temporary upload directory")
    return resolved


def cleanup_temp_files(directory: Path, dry_run: bool) -> list[Path]:
    """Remove regular, non-symlinked temporary files older than 24 hours."""

    root = _safe_temp_directory(directory)
    if not root.exists():
        return []
    cutoff = datetime.now(UTC) - timedelta(hours=24)
    removed: list[Path] = []
    for candidate in root.iterdir():
        if candidate.is_symlink() or not candidate.is_file():
            continue
        if datetime.fromtimestamp(candidate.stat().st_mtime, UTC) >= cutoff:
            continue
        removed.append(candidate)
        if not dry_run:
            candidate.unlink(missing_ok=True)
    return removed


async def mark_expired_uploads_deleted(session: AsyncSession, before: datetime) -> int:
    """Mark expired temporary upload metadata deleted without retaining raw-file references."""

    result = await session.execute(
        update(UploadObject)
        .where(UploadObject.expires_at < before, UploadObject.status != UploadStatus.DELETED)
        .values(status=UploadStatus.DELETED)
    )
    return int(getattr(result, "rowcount", 0) or 0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove expired temporary uploads")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()
    for path in cleanup_temp_files(arguments.directory, arguments.dry_run):
        print(path)


if __name__ == "__main__":
    main()
