import type { PropsWithChildren } from "react";
export function Table({ children }: PropsWithChildren): React.JSX.Element { return <div className="table-wrap"><table>{children}</table></div>; }
