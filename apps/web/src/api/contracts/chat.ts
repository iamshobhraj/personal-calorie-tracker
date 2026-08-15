import type { IsoDateTime, UUID } from "./common";
import type { MealUpsertInput } from "./meals";
export type ChatRole = "USER" | "ASSISTANT" | "TOOL";
export interface ChatSession { id: UUID; title: string | null; createdAt: IsoDateTime; updatedAt: IsoDateTime }
export interface MealDraftAction { type: "MEAL_DRAFT"; confirmationToken: string; draft: MealUpsertInput }
export interface ChatMessage { id: UUID; role: ChatRole; content: string; createdAt: IsoDateTime; actions: MealDraftAction[] }
export interface ChatMessageResult { userMessageId: UUID; assistantMessage: ChatMessage; actions: MealDraftAction[] }
