import type { UUID } from "./common";
export interface SignupInput { email: string; password: string; displayName: string; timezone: string }
export interface LoginInput { email: string; password: string }
export interface AuthUser { id: UUID; displayName: string | null; timezone: string }
export interface LoginResult { accessToken: string; expiresIn: number; tokenType: "Bearer"; user: AuthUser }
export interface AccessTokenResult { accessToken: string; expiresIn: number; tokenType: "Bearer" }
