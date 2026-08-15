import type { PropsWithChildren } from "react";
export function EmptyState({ children }: PropsWithChildren): React.JSX.Element { return <div className="empty">{children}</div>; }
