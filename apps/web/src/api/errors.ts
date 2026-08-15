import type { ApiErrorDetail } from "./contracts/common";
export class ApiError extends Error {
  constructor(public readonly status: number, public readonly code: string, message: string, public readonly details: ApiErrorDetail[] = [], public readonly requestId?: string, public readonly retryAfter?: number) { super(message); this.name = "ApiError"; }
}
