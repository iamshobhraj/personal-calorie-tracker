import type { ApiErrorDetail, UUID } from "./common";
import type { MealUpsertInput } from "./meals";
export type PdfImportStatus = "PROCESSING" | "READY" | "COMMITTED" | "FAILED" | "CANCELLED";
export type PdfImportValidity = "ALL" | "VALID" | "INVALID";
export interface PdfImportSummary { totalRows: number; validRows: number; invalidRows: number }
export interface PdfImportResource { id: UUID; status: PdfImportStatus; summary: PdfImportSummary }
export interface PdfImportRow { rowId: number; sourceRowNumber: number; selected: boolean; parsedMeal: MealUpsertInput | null; validationErrors: ApiErrorDetail[]; committedMealId: UUID | null }
export interface PdfCommitResult { importId: UUID; status: "COMMITTED"; createdMealEntryIds: UUID[]; createdCount: number }
