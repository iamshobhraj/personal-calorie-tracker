from uuid import UUID

from pydantic import BaseModel, Field

from src.persistence.models.enums import PdfImportStatus


class PdfImportSummaryResource(BaseModel):
    total_rows: int = Field(alias="totalRows")
    valid_rows: int = Field(alias="validRows")
    invalid_rows: int = Field(alias="invalidRows")


class PdfImportResource(BaseModel):
    id: UUID
    status: PdfImportStatus
    summary: PdfImportSummaryResource
