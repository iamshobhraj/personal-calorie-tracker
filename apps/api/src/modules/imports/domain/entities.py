from dataclasses import dataclass


@dataclass(frozen=True)
class ImportPreview:
    total_rows: int
    valid_rows: int
    invalid_rows: int
