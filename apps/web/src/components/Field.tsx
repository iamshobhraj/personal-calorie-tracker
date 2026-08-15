import type { InputHTMLAttributes } from "react";
export function Field({ label, error, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string | undefined }): React.JSX.Element { return <label className="field"><span>{label}</span><input {...props} />{error && <small role="alert">{error}</small>}</label>; }
