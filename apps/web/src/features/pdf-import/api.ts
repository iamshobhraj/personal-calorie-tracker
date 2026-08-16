import { apiRequest } from "../../api/client";
import type { MealUpsertInput } from "../../api/contracts/meals";
import { envelopeSchema, pageSchema } from "../../api/schemas/common";
import { pdfImportSchema, pdfRowSchema } from "../../api/schemas/pdfImports";
import { z } from "zod";

export function uploadPdf(file: File, timezone: string, defaultMealType?: string) { const form = new FormData(); form.set("file", file); form.set("timezone", timezone); if (defaultMealType) form.set("defaultMealType", defaultMealType); return apiRequest("/pdf-imports", { method: "POST", formData: form, schema: envelopeSchema(pdfImportSchema), idempotencyKey: crypto.randomUUID() }); }
export function getPdfImport(id: string) { return apiRequest(`/pdf-imports/${id}`, { schema: envelopeSchema(pdfImportSchema) }); }
export function getPdfRows(id: string) { return apiRequest(`/pdf-imports/${id}/rows?page=1&limit=100`, { schema: pageSchema(pdfRowSchema) }); }
export function updatePdfRow(importId: string, rowId: number, selected: boolean, parsedMeal: MealUpsertInput) { return apiRequest(`/pdf-imports/${importId}/rows/${rowId}`, { method: "PUT", body: { selected, parsedMeal }, schema: envelopeSchema(pdfRowSchema) }); }
export function commitPdfImport(importId: string, selectedRowIds: number[]) { return apiRequest(`/pdf-imports/${importId}/commit`, { method: "POST", body: { selectedRowIds }, schema: envelopeSchema(z.object({ importId: z.string().uuid(), status: z.literal("COMMITTED"), createdMealEntryIds: z.array(z.string().uuid()), createdCount: z.number() })), idempotencyKey: crypto.randomUUID() }); }
