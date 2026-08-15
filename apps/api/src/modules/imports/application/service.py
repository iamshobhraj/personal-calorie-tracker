from src.modules.imports.domain.entities import ImportPreview


def preview_summary(total_rows: int, valid_rows: int) -> ImportPreview:
    return ImportPreview(total_rows, valid_rows, total_rows - valid_rows)
