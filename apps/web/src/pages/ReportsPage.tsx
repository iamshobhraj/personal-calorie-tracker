import { useState } from "react";
import { useQueries } from "@tanstack/react-query";

import { CalorieTrendChart } from "../charts/CalorieTrendChart";
import { MacroChart } from "../charts/MacroChart";
import { MicronutrientChart } from "../charts/MicronutrientChart";
import { ReportFilters } from "../features/reports/ReportFilters";
import { reports } from "../features/reports/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function ReportsPage(): React.JSX.Element {
  useDocumentTitle("Nutrition Reports");
  const today = new Date();
  const week = new Date(today);
  week.setDate(today.getDate() - 6);

  const [from, setFrom] = useState(week.toISOString().slice(0, 10));
  const [to, setTo] = useState(today.toISOString().slice(0, 10));
  const query = `dateFrom=${from}&dateTo=${to}&interval=DAY&page=1&limit=100`;

  const [calories, macros, micros] = useQueries({
    queries: [
      {
        queryKey: ["reports", "calories", query],
        queryFn: () => reports(query).calories,
      },
      {
        queryKey: ["reports", "macros", query],
        queryFn: () => reports(query).macros,
      },
      {
        queryKey: ["reports", "micros", query],
        queryFn: () => reports(query).micronutrients,
      },
    ],
  });

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Nutrition Reports & Analytics</h1>
          <p className="page-subtitle">
            View detailed historical trends for energy intake, macro balance, and micronutrient coverage.
          </p>
        </div>
      </div>

      <ReportFilters from={from} to={to} onFrom={setFrom} onTo={setTo} />

      <div className="reports-grid">
        <section className="report-card card">
          <h2 className="report-card__title">🔥 Daily Calorie Intake Trend</h2>
          <p className="form-subtitle">Track daily energy balance against your health goals.</p>
          {calories.data ? (
            <CalorieTrendChart data={calories.data.data} />
          ) : (
            <div className="loading-placeholder">Loading calorie chart…</div>
          )}
        </section>

        <section className="report-card card">
          <h2 className="report-card__title">⚖️ Macronutrient Breakdown</h2>
          <p className="form-subtitle">Ratio of energy from Protein (4 kcal/g), Carbs (4 kcal/g), and Fat (9 kcal/g).</p>
          {macros.data ? (
            <MacroChart data={macros.data.data} />
          ) : (
            <div className="loading-placeholder">Loading macro chart…</div>
          )}
        </section>

        <section className="report-card card report-card--full-width">
          <h2 className="report-card__title">🧪 Micronutrient Intake Summary</h2>
          <p className="form-subtitle">Daily average vitamin and mineral coverage over the selected time period.</p>
          {micros.data ? (
            <MicronutrientChart data={micros.data.data} />
          ) : (
            <div className="loading-placeholder">Loading micronutrient data…</div>
          )}
        </section>
      </div>
    </div>
  );
}
