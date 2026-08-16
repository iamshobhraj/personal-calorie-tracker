import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { CalorieTrendPoint } from "../api/contracts/reports";

interface CalorieTrendChartProps {
  data: CalorieTrendPoint[];
  calorieTarget?: number | undefined;
}

interface CustomTooltipProps {
  active?: boolean | undefined;
  payload?: Array<{ value: number }> | undefined;
  label?: string | undefined;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (active && payload && payload.length) {
    const val = payload[0]?.value;
    return (
      <div className="chart-tooltip">
        <p className="chart-tooltip__label">{label}</p>
        <p className="chart-tooltip__value">
          <span className="chart-tooltip__dot" style={{ backgroundColor: "#10b981" }} />
          <strong>{val !== undefined ? `${val.toLocaleString()} kcal` : "No data"}</strong>
        </p>
      </div>
    );
  }
  return null;
}

export function CalorieTrendChart({
  data,
  calorieTarget,
}: CalorieTrendChartProps): React.JSX.Element {
  const chartData = data.map((point) => ({
    date: point.periodStart,
    calories: point.calories,
  }));

  const knownDays = data.filter((point) => point.calories !== null).length;

  if (!data.length) {
    return <div className="loading-placeholder">No calorie data in this time period.</div>;
  }

  return (
    <div className="chart-wrapper">
      <div style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 15, right: 15, left: -15, bottom: 5 }}>
            <defs>
              <linearGradient id="calorieGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis
              dataKey="date"
              stroke="#94a3b8"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: string) => {
                const parts = v.split("-");
                return parts.length === 3 ? `${parts[1]}/${parts[2]}` : v;
              }}
            />
            <YAxis
              stroke="#94a3b8"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => `${v}`}
            />
            <Tooltip content={<CustomTooltip />} />
            {calorieTarget ? (
              <ReferenceLine
                y={calorieTarget}
                stroke="#6366f1"
                strokeDasharray="4 4"
                label={{
                  value: `Target: ${calorieTarget} kcal`,
                  fill: "#6366f1",
                  fontSize: 11,
                  position: "insideTopRight",
                }}
              />
            ) : null}
            <Area
              type="monotone"
              dataKey="calories"
              stroke="#10b981"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#calorieGrad)"
              dot={{ fill: "#10b981", r: 3.5, strokeWidth: 1.5, stroke: "#ffffff" }}
              activeDot={{ r: 6, fill: "#059669", stroke: "#ffffff", strokeWidth: 2 }}
              connectNulls={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-footer-note">
        {knownDays <= 1 ? (
          <span>Log meals across multiple days to view a connected trendline.</span>
        ) : (
          <span>Showing intake across {knownDays} logged day{knownDays > 1 ? "s" : ""}.</span>
        )}
      </div>
    </div>
  );
}
