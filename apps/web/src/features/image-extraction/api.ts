import { apiRequest } from "../../api/client";
import type { ImageKind } from "../../api/contracts/common";
import { envelopeSchema } from "../../api/schemas/common";
import { extractionSchema } from "../../api/schemas/extractions";

export function analyzeImage(file: File, imageKind: ImageKind, signal?: AbortSignal) {
  const form = new FormData(); form.set("file", file); form.set("imageKind", imageKind);
  return apiRequest("/nutrition-extractions", { method: "POST", formData: form, schema: envelopeSchema(extractionSchema), idempotencyKey: crypto.randomUUID(), signal });
}
