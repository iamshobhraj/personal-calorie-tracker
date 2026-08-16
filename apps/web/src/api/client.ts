import { z } from "zod";
import { ApiError } from "./errors";

let getToken: () => string | null = () => null;
let onTerminalAuth: () => void = () => undefined;
let updateToken: (accessToken: string) => void = () => undefined;
let refreshPromise: Promise<string | null> | null = null;

export function configureApiAuth(
  accessor: () => string | null,
  terminal: () => void,
  updater: (accessToken: string) => void
): void {
  getToken = accessor;
  onTerminalAuth = terminal;
  updateToken = updater;
}

export interface RequestOptions<T> {
  method?: "GET" | "POST" | "PUT" | "DELETE" | undefined;
  body?: unknown;
  formData?: FormData | undefined;
  schema: z.ZodType<T>;
  authenticated?: boolean | undefined;
  accessToken?: string | undefined;
  idempotencyKey?: string | undefined;
  signal?: AbortSignal | undefined;
  headers?: Record<string, string> | undefined;
}

async function refresh(): Promise<string | null> {
  if (refreshPromise === null) refreshPromise = fetch("/api/v1/auth/refresh", { method: "POST", credentials: "include", headers: { Accept: "application/json", "Content-Type": "application/json" }, body: "{}" }).then(async response => {
    if (!response.ok) return null;
    const payload: unknown = await response.json();
    const parsed = z.object({ data: z.object({ accessToken: z.string() }) }).safeParse(payload);
    if (!parsed.success) return null;
    updateToken(parsed.data.data.accessToken);
    return parsed.data.data.accessToken;
  }).finally(() => { refreshPromise = null; });
  return refreshPromise;
}

export async function apiRequest<T>(path: string, options: RequestOptions<T>): Promise<T> {
  const send = async (retry: boolean): Promise<T> => {
    const headers = new Headers({ Accept: "application/json" });
    if (options.headers) {
      for (const [k, v] of Object.entries(options.headers)) {
        headers.set(k, v);
      }
    }
    if (options.body !== undefined) headers.set("Content-Type", "application/json");
    if (options.authenticated !== false) { const token = options.accessToken ?? getToken(); if (token) headers.set("Authorization", `Bearer ${token}`); }
    if (options.idempotencyKey) headers.set("Idempotency-Key", options.idempotencyKey);
    const init: RequestInit = { method: options.method ?? "GET", headers, credentials: "include" };
    if (options.signal !== undefined) init.signal = options.signal;
    const body = options.formData ?? (options.body === undefined ? undefined : JSON.stringify(options.body));
    if (body !== undefined) init.body = body;
    const response = await fetch(`/api/v1${path}`, init);
    const raw: unknown = await response.json().catch(() => null);
    if (response.status === 401 && options.authenticated !== false && retry) { const token = await refresh(); if (token) return send(false); onTerminalAuth(); }
    if (!response.ok) { const error = z.object({ error: z.object({ code: z.string(), message: z.string(), details: z.array(z.object({ field: z.string().nullable().optional(), code: z.string(), message: z.string() })).default([]) }), meta: z.object({ requestId: z.string() }).optional() }).safeParse(raw); const details = error.success ? error.data.error.details.map(item => item.field === undefined ? { code: item.code, message: item.message } : { field: item.field, code: item.code, message: item.message }) : []; throw new ApiError(response.status, error.success ? error.data.error.code : "HTTP_ERROR", error.success ? error.data.error.message : "The request could not be completed.", details, error.success ? error.data.meta?.requestId : undefined, Number(response.headers.get("Retry-After")) || undefined); }
    const parsed = options.schema.safeParse(raw);
    if (!parsed.success) throw new ApiError(0, "CLIENT_CONTRACT_ERROR", "The server returned an unexpected response.");
    return parsed.data;
  };
  return send(true);
}
