import type { PropsWithChildren } from "react";
export function Card({ children }: PropsWithChildren): React.JSX.Element { return <section className="card">{children}</section>; }
