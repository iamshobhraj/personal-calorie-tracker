import hashlib
import json
from uuid import UUID


def canonical_hash(method: str, path: str, subject: UUID | str, body: object) -> str:
    payload = {"method": method, "path": path, "subject": str(subject), "body": body}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()
