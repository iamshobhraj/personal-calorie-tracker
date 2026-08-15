import type { UUID } from "./common";
export interface Profile { id: UUID; email: string | null; displayName: string | null; timezone: string }
export interface ProfileUpdateInput { displayName: string; timezone: string }
