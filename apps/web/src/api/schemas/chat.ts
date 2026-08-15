import { z } from "zod";
export const chatSessionSchema = z.object({ id: z.string().uuid(), title: z.string().nullable(), createdAt: z.string(), updatedAt: z.string() });
export const chatMessageSchema = z.object({ id: z.string().uuid(), role: z.enum(["USER", "ASSISTANT", "TOOL"]), content: z.string(), createdAt: z.string(), actions: z.array(z.unknown()).default([]) });
