import { z } from "zod";
export const loginInputSchema = z.object({ email: z.string().email("Enter a valid email."), password: z.string().min(1, "Enter your password.") });
export const signupInputSchema = loginInputSchema.extend({ password: z.string().min(12, "Use at least 12 characters."), displayName: z.string().min(1, "Enter a name."), timezone: z.string().min(1) });
