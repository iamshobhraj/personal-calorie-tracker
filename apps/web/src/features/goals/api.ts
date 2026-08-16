import { z } from "zod"; import { apiRequest } from "../../api/client"; import type { GoalCreateInput } from "../../api/contracts/goals"; import { envelopeSchema, pageSchema } from "../../api/schemas/common"; import { nutrientCodeSchema } from "../../api/schemas/resources"; import { generateUuid } from "../../utils/uuid";
const target = z.object({ nutrientCode: nutrientCodeSchema, targetAmount: z.number(), unit: z.enum(["kcal", "g", "mg", "mcg"]), targetKind: z.enum(["TARGET", "MINIMUM", "MAXIMUM"]) }); const goal = z.object({ id:z.string().uuid(),name:z.string(),effectiveFrom:z.string(),effectiveTo:z.string().nullable(),targetWeightKg:z.number().nullable(),status:z.enum(["ACTIVE","ARCHIVED"]),targets:z.array(target),createdAt:z.string(),updatedAt:z.string() });
export const getGoals = () => apiRequest("/goals?status=ACTIVE", { schema: pageSchema(goal) });
export const getCurrentGoal = (onDate?: string) =>
  apiRequest(onDate ? `/goals/current?onDate=${onDate}` : "/goals/current", {
    schema: envelopeSchema(goal),
  });
export const createGoal = (input: GoalCreateInput) =>
  apiRequest("/goals", {
    method: "POST",
    body: input,
    schema: envelopeSchema(goal),
    idempotencyKey: generateUuid(),
  });
export const deleteGoal = (id: string) =>
  apiRequest(`/goals/${id}`, {
    method: "DELETE",
    schema: envelopeSchema(z.object({ id: z.string(), status: z.literal("ARCHIVED") })),
  });
