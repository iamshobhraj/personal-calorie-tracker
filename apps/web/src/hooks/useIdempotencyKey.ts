import { useRef } from "react";
import { generateUuid } from "../utils/uuid";
export function useIdempotencyKey(): () => string { const key = useRef(generateUuid()); return () => key.current; }
