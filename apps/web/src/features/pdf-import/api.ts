import { apiRequest } from "../../api/client";
import { envelopeSchema } from "../../api/schemas/common";
import { pdfImportSchema } from "../../api/schemas/pdfImports";
export function uploadPdf(file: File, timezone: string, defaultMealType?: string) { const form = new FormData(); form.set("file", file); form.set("timezone", timezone); if (defaultMealType) form.set("defaultMealType", defaultMealType); return apiRequest("/pdf-imports", { method: "POST", formData: form, schema: envelopeSchema(pdfImportSchema), idempotencyKey: crypto.randomUUID() }); }
export function getPdfImport(id: string) { return apiRequest(`/pdf-imports/${id}`, { schema: envelopeSchema(pdfImportSchema) }); }
