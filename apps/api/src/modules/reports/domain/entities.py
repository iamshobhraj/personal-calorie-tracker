from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ReportPeriod:
    start: date
    end: date
