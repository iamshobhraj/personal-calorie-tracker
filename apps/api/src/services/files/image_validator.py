from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from src.shared.errors.api_error import ApiError


@dataclass(frozen=True, slots=True)
class ValidatedImage:
    path: Path
    mime_type: str
    sha256_hex: str
    byte_size: int


_MAGIC = {b"\xff\xd8\xff": "image/jpeg", b"\x89PNG\r\n\x1a\n": "image/png", b"RIFF": "image/webp"}


async def validate_image(
    upload: UploadFile, directory: Path, max_bytes: int, max_pixels: int
) -> ValidatedImage:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{secrets.token_hex(32)}.upload"
    digest, size = hashlib.sha256(), 0
    try:
        with path.open("xb") as destination:
            while chunk := await upload.read(64 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise ApiError(
                        413, "FILE_TOO_LARGE", "The image exceeds the maximum permitted size."
                    )
                digest.update(chunk)
                destination.write(chunk)
        if size == 0:
            raise ApiError(
                415, "UNSUPPORTED_MEDIA_TYPE", "The uploaded file is not a supported image."
            )
        raw = path.read_bytes()
        mime = next((kind for magic, kind in _MAGIC.items() if raw.startswith(magic)), None)
        if mime == "image/webp" and raw[8:12] != b"WEBP":
            mime = None
        if mime is None:
            raise ApiError(
                415, "UNSUPPORTED_MEDIA_TYPE", "The uploaded file is not a supported image."
            )
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                if getattr(image, "is_animated", False) or image.width * image.height > max_pixels:
                    raise ApiError(
                        415, "UNSUPPORTED_MEDIA_TYPE", "The uploaded image is not permitted."
                    )
                format_mime = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}.get(
                    image.format or ""
                )
                if format_mime != mime:
                    raise ApiError(
                        415, "UNSUPPORTED_MEDIA_TYPE", "The uploaded image type is inconsistent."
                    )
        except (UnidentifiedImageError, OSError) as exc:
            raise ApiError(
                415, "UNSUPPORTED_MEDIA_TYPE", "The uploaded file is not a valid image."
            ) from exc
        return ValidatedImage(path, mime, digest.hexdigest(), size)
    except BaseException:
        path.unlink(missing_ok=True)
        raise
