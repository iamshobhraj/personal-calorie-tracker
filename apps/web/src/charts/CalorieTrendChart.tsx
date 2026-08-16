import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { CalorieTrendPoint } from "../api/contracts/reports";
import { ChartFrame } from "./ChartFrame";

export function CalorieTrendChart({ data }: { data: CalorieTrendPoint[] }): React.JSX.Element {
  const knownDays = data.filter((point) => point.calories !== null).length;
  return <ChartFrame title="Calorie trend"><ResponsiveContainer width="100%" height={250}><LineChart data={data}><XAxis dataKey="periodStart" /><YAxis /><Tooltip /><Line dataKey="calories" stroke="#126b54" connectNulls={false} dot={{ r: 4 }} /></LineChart></ResponsiveContainer>{knownDays === 1 && <p>One day has calorie data. Add meals on another day to draw a trend line.</p>}<p>Missing values are unknown, not zero.</p></ChartFrame>;
}
