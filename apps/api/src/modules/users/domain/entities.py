from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserIdentity:
    id: UUID
    email: str
    display_name: str
    timezone: str
