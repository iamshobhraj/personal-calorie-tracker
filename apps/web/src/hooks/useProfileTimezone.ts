import { useAuth } from "../state/auth/AuthContext";
export function useProfileTimezone(): string { const { state } = useAuth(); return state.status === "authenticated" ? state.user.timezone : "UTC"; }
