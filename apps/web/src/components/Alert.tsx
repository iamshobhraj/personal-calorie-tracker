import type { PropsWithChildren } from "react";
export function Alert({ children }: PropsWithChildren): React.JSX.Element { return <p className="alert" role="alert">{children}</p>; }
