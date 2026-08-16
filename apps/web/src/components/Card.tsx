import type { ReactNode } from "react";

export interface CardProps {
  children?: ReactNode;
  className?: string;
}

export function Card({ children, className = "" }: CardProps): React.JSX.Element {
  return <section className={`card ${className}`.trim()}>{children}</section>;
}
