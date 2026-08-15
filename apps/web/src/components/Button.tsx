import type { ButtonHTMLAttributes } from "react";
export function Button({ className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement>): React.JSX.Element { return <button className={`button ${className}`} {...props} />; }
