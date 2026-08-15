import { useRef } from "react";
export function useIdempotencyKey(): () => string { const key = useRef(crypto.randomUUID()); return () => key.current; }
