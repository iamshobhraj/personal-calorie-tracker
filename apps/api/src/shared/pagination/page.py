from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True, slots=True)
class Page:
    page: int
    limit: int
    total_items: int

    @property
    def total_pages(self) -> int:
        return ceil(self.total_items / self.limit) if self.total_items else 0

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1 and self.total_items > 0
