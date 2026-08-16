import type { ButtonHTMLAttributes, ReactNode } from "react";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "outline" | "ghost";
  size?: "small" | "medium" | "large";
  isLoading?: boolean;
  children?: ReactNode;
}

export function Button({
  className = "",
  variant = "primary",
  size = "medium",
  isLoading = false,
  disabled,
  children,
  ...props
}: ButtonProps): React.JSX.Element {
  return (
    <button
      className={`btn btn--${variant} btn--${size} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="btn__loading">
          <span className="spinner" />
          <span>Processing…</span>
        </span>
      ) : (
        children
      )}
    </button>
  );
}
