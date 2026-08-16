import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MacroPoint } from "../api/contracts/reports";

interface MacroChartProps {
  data: MacroPoint[];
}

interface CustomTooltipProps {
  active?: boolean | undefined;
  payload?: Array<{ name: string; value: number; color: string; payload: unknown }> | undefined;
  label?: string | undefined;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <p className="chart-tooltip__label">{label}</p>
        <div className="chart-tooltip__macros">
          {payload.map((entry) => (
            <div key={entry.name} className="chart-tooltip__macro-row">
              <span className="chart-tooltip__dot" style={{ backgroundColor: entry.color }} />
              <span className="chart-tooltip__macro-name">
                {entry.name.charAt(0).toUpperCase() + entry.name.slice(1)}:
              </span>
              <strong>{entry.value} g</strong>
            </div>
          ))}
        </div>
      </div>
    );
  }
  return null;
}

export function MacroChart({ data }: MacroChartProps): React.JSX.Element {
  const chartData = data.map((p) => ({
    date: p.periodStart,
    protein: Math.round((p.totals.protein.amount ?? 0) * 10) / 10,
    carbohydrate: Math.round((p.totals.carbohydrate.amount ?? 0) * 10) / 10,
    fat: Math.round((p.totals.fat.amount ?? 0) * 10) / 10,
  }));

  if (!data.length) {
    return <div className="loading-placeholder">No macronutrient data in this time period.</div>;
  }

  return (
    <div className="chart-wrapper">
      <div style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 15, right: 15, left: -15, bottom: 5 }}>
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
              tickFormatter={(v: number) => `${v}g`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="protein" name="Protein" fill="#3b82f6" radius={[4, 4, 0, 0]} maxBarSize={28} />
            <Bar
              dataKey="carbohydrate"
              name="Carbs"
              fill="#f59e0b"
              radius={[4, 4, 0, 0]}
              maxBarSize={28}
            />
            <Bar dataKey="fat" name="Fat" fill="#ec4899" radius={[4, 4, 0, 0]} maxBarSize={28} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="macro-legend-pills">
        <div className="macro-pill macro-pill--protein">
          <span className="macro-pill__dot" /> Protein (g)
        </div>
        <div className="macro-pill macro-pill--carbs">
          <span className="macro-pill__dot" /> Carbs (g)
        </div>
        <div className="macro-pill macro-pill--fat">
          <span className="macro-pill__dot" /> Fat (g)
        </div>
      </div>
    </div>
  );
}
