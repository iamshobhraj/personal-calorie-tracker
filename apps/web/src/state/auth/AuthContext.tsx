import { createContext, useCallback, useContext, useEffect, useMemo, useState, type PropsWithChildren } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { apiRequest, configureApiAuth } from "../../api/client";
import type { AuthUser, LoginInput, SignupInput } from "../../api/contracts/auth";
import { envelopeSchema } from "../../api/schemas/common";
import { profileSchema } from "../../api/schemas/resources";
import { z } from "zod";

type AuthState = { status: "initializing" } | { status: "anonymous" } | { status: "authenticated"; accessToken: string; user: AuthUser };
interface AuthContextValue { state: AuthState; login(input: LoginInput): Promise<void>; signup(input: SignupInput): Promise<void>; logout(): Promise<void> }
const AuthContext = createContext<AuthContextValue | null>(null);
const loginSchema = envelopeSchema(z.object({ accessToken: z.string(), expiresIn: z.number(), tokenType: z.literal("Bearer"), user: z.object({ id: z.string().uuid(), displayName: z.string().nullable(), timezone: z.string() }) }));
const tokenSchema = envelopeSchema(z.object({ accessToken: z.string(), expiresIn: z.number(), tokenType: z.literal("Bearer") }));

export function AuthProvider({ children }: PropsWithChildren): React.JSX.Element {
  const [state, setState] = useState<AuthState>({ status: "initializing" }); const queries = useQueryClient();
  const clear = useCallback(() => { queries.clear(); setState({ status: "anonymous" }); }, [queries]);
  useEffect(() => { configureApiAuth(() => state.status === "authenticated" ? state.accessToken : null, clear, accessToken => { setState(current => current.status === "authenticated" ? { ...current, accessToken } : current); }); }, [state, clear]);
  useEffect(() => { void apiRequest("/auth/refresh", { method: "POST", body: {}, schema: tokenSchema, authenticated: false }).then(async token => { const profile = await apiRequest("/profile", { schema: envelopeSchema(profileSchema) }); setState({ status: "authenticated", accessToken: token.data.accessToken, user: { id: profile.data.id, displayName: profile.data.displayName, timezone: profile.data.timezone } }); }).catch(() => { setState({ status: "anonymous" }); }); }, []);
  const value = useMemo<AuthContextValue>(() => ({ state, login: async input => { const result = await apiRequest("/auth/login", { method: "POST", body: input, schema: loginSchema, authenticated: false }); setState({ status: "authenticated", accessToken: result.data.accessToken, user: result.data.user }); }, signup: async input => { await apiRequest("/auth/signup", { method: "POST", body: input, schema: envelopeSchema(z.object({ userId: z.uuid(), status: z.literal("ACTIVE") })), authenticated: false, idempotencyKey: crypto.randomUUID() }); }, logout: async () => { try { await apiRequest("/auth/logout", { method: "POST", body: {}, schema: envelopeSchema(z.object({ status: z.literal("LOGGED_OUT") })) }); } finally { clear(); } } }), [state, clear]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth(): AuthContextValue { const value = useContext(AuthContext); if (!value) throw new Error("AuthProvider is required"); return value; }
