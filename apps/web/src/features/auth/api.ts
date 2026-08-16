import { z } from "zod";
import { apiRequest } from "../../api/client";
import type { SignupInput } from "../../api/contracts/auth";
import { envelopeSchema } from "../../api/schemas/common";
import { generateUuid } from "../../utils/uuid";
const loginData = z.object({ accessToken: z.string(), expiresIn: z.number(), tokenType: z.literal("Bearer"), user: z.object({ id: z.string().uuid(), displayName: z.string().nullable(), timezone: z.string() }) });
export const signup = (input: SignupInput) => apiRequest("/auth/signup", { method: "POST", body: input, schema: envelopeSchema(z.object({ userId: z.string().uuid(), status: z.literal("ACTIVE") })), authenticated: false, idempotencyKey: generateUuid() });
export const login = (email: string, password: string) => apiRequest("/auth/login", { method: "POST", body: { email, password }, schema: envelopeSchema(loginData), authenticated: false });
