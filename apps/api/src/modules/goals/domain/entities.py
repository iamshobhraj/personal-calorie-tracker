from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class GoalPeriod:
    effective_from: date
    effective_to: date | None
