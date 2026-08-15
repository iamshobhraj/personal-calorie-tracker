export function Stat({ label, value }: { label: string; value: string }): React.JSX.Element { return <div className="stat"><span>{label}</span><strong>{value}</strong></div>; }
