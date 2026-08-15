import { z } from "zod";
export const pdfImportSchema = z.object({ id: z.string().uuid(), status: z.enum(["PROCESSING", "READY", "COMMITTED", "FAILED", "CANCELLED"]), summary: z.object({ totalRows: z.number(), validRows: z.number(), invalidRows: z.number() }) });
export const pdfRowSchema = z.object({ rowId: z.number(), sourceRowNumber: z.number(), selected: z.boolean(), parsedMeal: z.unknown().nullable(), validationErrors: z.array(z.unknown()), committedMealId: z.string().uuid().nullable() });
