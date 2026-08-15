from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader

from src.shared.errors.api_error import ApiError


@dataclass(frozen=True, slots=True)
class ValidatedPdf:
    path: Path
    sha256_hex: str
    byte_size: int
    pages: int


async def validate_pdf(
    upload: UploadFile, directory: Path, max_bytes: int, max_pages: int
) -> ValidatedPdf:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{secrets.token_hex(32)}.upload"
    size, digest = 0, hashlib.sha256()
    try:
        with path.open("xb") as destination:
            while chunk := await upload.read(64 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise ApiError(
                        413, "FILE_TOO_LARGE", "The PDF exceeds the maximum permitted size."
                    )
                digest.update(chunk)
                destination.write(chunk)
        if size == 0 or path.read_bytes()[:5] != b"%PDF-":
            raise ApiError(415, "UNSUPPORTED_MEDIA_TYPE", "The uploaded file is not a valid PDF.")
        try:
            reader = PdfReader(str(path), strict=True)
            if reader.is_encrypted:
                raise ApiError(415, "UNSUPPORTED_PDF", "Encrypted PDFs are not supported.")
            pages = len(reader.pages)
        except ApiError:
            raise
        except Exception as exc:
            raise ApiError(
                415, "UNSUPPORTED_PDF", "The uploaded file is not a readable PDF."
            ) from exc
        if pages < 1 or pages > max_pages:
            raise ApiError(
                422, "PDF_PAGE_LIMIT", "The PDF page count is outside the permitted range."
            )
        return ValidatedPdf(path, digest.hexdigest(), size, pages)
    except BaseException:
        path.unlink(missing_ok=True)
        raise
