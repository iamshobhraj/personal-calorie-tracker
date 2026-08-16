import { z } from "zod";
import { apiRequest } from "../../api/client";
import { envelopeSchema } from "../../api/schemas/common";
import { chatMessageSchema, chatSessionSchema } from "../../api/schemas/chat";
import { generateUuid } from "../../utils/uuid";

export function createChatSession(title?: string) { return apiRequest("/chat/sessions", { method: "POST", body: { title: title ?? null }, schema: envelopeSchema(chatSessionSchema), idempotencyKey: generateUuid() }); }
export function listChatSessions() { return apiRequest("/chat/sessions", { schema: envelopeSchema(chatSessionSchema.array()) }); }
export function listChatMessages(id: string) { return apiRequest(`/chat/sessions/${id}/messages`, { schema: envelopeSchema(chatMessageSchema.array()) }); }
export function sendChatMessage(id: string, message: string, timezone: string) { return apiRequest(`/chat/sessions/${id}/messages`, { method: "POST", body: { message, timezone }, schema: envelopeSchema(z.object({ userMessageId: z.string(), assistantMessage: chatMessageSchema, actions: z.array(z.unknown()) })), idempotencyKey: generateUuid() }); }
