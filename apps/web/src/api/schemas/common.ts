import { z } from "zod";
export const metaSchema = z.object({ requestId: z.string(), timezone: z.string().nullable().optional(), filters: z.record(z.string(), z.unknown()).nullable().optional() });
export const envelopeSchema = <T extends z.ZodType>(data: T) => z.object({ data, meta: metaSchema });
export const pageSchema = <T extends z.ZodType>(data: T) => z.object({ data: z.array(data), pagination: z.object({ page: z.number(), limit: z.number(), totalItems: z.number(), totalPages: z.number(), hasNext: z.boolean(), hasPrevious: z.boolean() }), meta: metaSchema });
