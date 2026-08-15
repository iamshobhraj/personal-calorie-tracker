from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class MealDateRange:
    date_from: date
    date_to: date
