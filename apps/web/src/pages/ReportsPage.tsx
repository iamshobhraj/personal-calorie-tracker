import { useState } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import { Flame, Beef, Wheat, Droplet, CalendarCheck2 } from "lucide-react";

import { CalorieTrendChart } from "../charts/CalorieTrendChart";
import { MacroChart } from "../charts/MacroChart";
import { MicronutrientChart } from "../charts/MicronutrientChart";
import { ReportFilters } from "../features/reports/ReportFilters";
import { reports } from "../features/reports/api";
import { getCurrentGoal } from "../features/goals/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useProfileTimezone } from "../hooks/useProfileTimezone";
import { localDateString } from "../utils/zonedDateTime";

export function ReportsPage(): React.JSX.Element {
  useDocumentTitle("Nutrition Reports");
  const timezone = useProfileTimezone();
  const today = new Date();
  const week = new Date(today);
  week.setDate(today.getDate() - 6);

  const [from, setFrom] = useState(localDateString(week, timezone));
  const [to, setTo] = useState(localDateString(today, timezone));
  const query = `dateFrom=${from}&dateTo=${to}&interval=DAY&page=1&limit=100`;

  const goal = useQuery({
    queryKey: ["goal", "current", to],
    queryFn: () => getCurrentGoal(to),
  });

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

  // Calculate high-level summary KPIs
  const caloriePoints = calories.data?.data ?? [];
  const loggedCalorieDays = caloriePoints.filter((p) => p.calories !== null);
  const totalCaloriesLogged = loggedCalorieDays.reduce((acc, p) => acc + (p.calories ?? 0), 0);
  const avgDailyCalories =
    loggedCalorieDays.length > 0
      ? Math.round(totalCaloriesLogged / loggedCalorieDays.length)
      : null;

  const macroPoints = macros.data?.data ?? [];
  const loggedMacroDays = macroPoints.filter(
    (p) =>
      p.totals.protein.amount !== null ||
      p.totals.carbohydrate.amount !== null ||
      p.totals.fat.amount !== null
  );

  const totalProtein = loggedMacroDays.reduce(
    (acc, p) => acc + (p.totals.protein.amount ?? 0),
    0
  );
  const totalCarbs = loggedMacroDays.reduce(
    (acc, p) => acc + (p.totals.carbohydrate.amount ?? 0),
    0
  );
  const totalFat = loggedMacroDays.reduce((acc, p) => acc + (p.totals.fat.amount ?? 0), 0);

  const avgProtein =
    loggedMacroDays.length > 0
      ? Math.round((totalProtein / loggedMacroDays.length) * 10) / 10
      : null;
  const avgCarbs =
    loggedMacroDays.length > 0
      ? Math.round((totalCarbs / loggedMacroDays.length) * 10) / 10
      : null;
  const avgFat =
    loggedMacroDays.length > 0 ? Math.round((totalFat / loggedMacroDays.length) * 10) / 10 : null;

  const calorieTarget = goal.data?.data.targets.find(
    (t) => t.nutrientCode === "ENERGY_KCAL"
  )?.targetAmount;

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

      {/* Preset and Date Range Filter Bar */}
      <ReportFilters from={from} to={to} onFrom={setFrom} onTo={setTo} timezone={timezone} />

      {/* KPI Summary Cards */}
      <div className="reports-kpi-grid">
        <div className="report-kpi-card card">
          <div className="report-kpi-icon report-kpi-icon--calories">
            <Flame size={20} />
          </div>
          <div className="report-kpi-content">
            <span className="report-kpi-label">Avg Daily Intake</span>
            <div className="report-kpi-value-row">
              <span className="report-kpi-value">
                {avgDailyCalories !== null ? avgDailyCalories.toLocaleString() : "—"}
              </span>
              <span className="report-kpi-unit">kcal / day</span>
            </div>
            {calorieTarget && avgDailyCalories ? (
              <span className="report-kpi-sub">
                {avgDailyCalories <= calorieTarget
                  ? `${calorieTarget - avgDailyCalories} kcal under target (${calorieTarget})`
                  : `${avgDailyCalories - calorieTarget} kcal over target (${calorieTarget})`}
              </span>
            ) : (
              <span className="report-kpi-sub">
                {loggedCalorieDays.length} day{loggedCalorieDays.length === 1 ? "" : "s"} logged
              </span>
            )}
          </div>
        </div>

        <div className="report-kpi-card card">
          <div className="report-kpi-icon report-kpi-icon--protein">
            <Beef size={20} />
          </div>
          <div className="report-kpi-content">
            <span className="report-kpi-label">Avg Protein</span>
            <div className="report-kpi-value-row">
              <span className="report-kpi-value">{avgProtein !== null ? avgProtein : "—"}</span>
              <span className="report-kpi-unit">g / day</span>
            </div>
            <span className="report-kpi-sub">
              {avgProtein ? `${Math.round(avgProtein * 4)} kcal from protein` : "No protein logged"}
            </span>
          </div>
        </div>

        <div className="report-kpi-card card">
          <div className="report-kpi-icon report-kpi-icon--carbs">
            <Wheat size={20} />
          </div>
          <div className="report-kpi-content">
            <span className="report-kpi-label">Avg Carbohydrates</span>
            <div className="report-kpi-value-row">
              <span className="report-kpi-value">{avgCarbs !== null ? avgCarbs : "—"}</span>
              <span className="report-kpi-unit">g / day</span>
            </div>
            <span className="report-kpi-sub">
              {avgCarbs ? `${Math.round(avgCarbs * 4)} kcal from carbs` : "No carbs logged"}
            </span>
          </div>
        </div>

        <div className="report-kpi-card card">
          <div className="report-kpi-icon report-kpi-icon--fat">
            <Droplet size={20} />
          </div>
          <div className="report-kpi-content">
            <span className="report-kpi-label">Avg Fat</span>
            <div className="report-kpi-value-row">
              <span className="report-kpi-value">{avgFat !== null ? avgFat : "—"}</span>
              <span className="report-kpi-unit">g / day</span>
            </div>
            <span className="report-kpi-sub">
              {avgFat ? `${Math.round(avgFat * 9)} kcal from fat` : "No fat logged"}
            </span>
          </div>
        </div>

        <div className="report-kpi-card card">
          <div className="report-kpi-icon report-kpi-icon--consistency">
            <CalendarCheck2 size={20} />
          </div>
          <div className="report-kpi-content">
            <span className="report-kpi-label">Consistency</span>
            <div className="report-kpi-value-row">
              <span className="report-kpi-value">{loggedCalorieDays.length}</span>
              <span className="report-kpi-unit">/ {caloriePoints.length || 7} days</span>
            </div>
            <span className="report-kpi-sub">
              {caloriePoints.length > 0
                ? `${Math.round((loggedCalorieDays.length / caloriePoints.length) * 100)}% tracking adherence`
                : "No days in range"}
            </span>
          </div>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="reports-grid">
        <section className="report-section card">
          <div className="report-section__header">
            <div>
              <h2 className="report-section__title">Daily Calorie Intake Trend</h2>
              <p className="report-section__subtitle">
                Track daily energy intake fluctuations and adherence to calorie objectives.
              </p>
            </div>
          </div>
          {calories.isLoading ? (
            <div className="loading-placeholder">Loading calorie chart…</div>
          ) : calories.data ? (
            <CalorieTrendChart data={calories.data.data} calorieTarget={calorieTarget} />
          ) : (
            <div className="loading-placeholder">No calorie records found.</div>
          )}
        </section>

        <section className="report-section card">
          <div className="report-section__header">
            <div>
              <h2 className="report-section__title">Macronutrient Breakdown</h2>
              <p className="report-section__subtitle">
                Daily protein (4 kcal/g), carbohydrate (4 kcal/g), and dietary fat (9 kcal/g) intake.
              </p>
            </div>
          </div>
          {macros.isLoading ? (
            <div className="loading-placeholder">Loading macronutrient chart…</div>
          ) : macros.data ? (
            <MacroChart data={macros.data.data} />
          ) : (
            <div className="loading-placeholder">No macro records found.</div>
          )}
        </section>

        <section className="report-section card report-section--full-width">
          <div className="report-section__header">
            <div>
              <h2 className="report-section__title">Micronutrient Intake Summary</h2>
              <p className="report-section__subtitle">
                Daily average vitamin and mineral coverage over the selected time period.
              </p>
            </div>
          </div>
          {micros.isLoading ? (
            <div className="loading-placeholder">Loading micronutrient data…</div>
          ) : micros.data ? (
            <MicronutrientChart data={micros.data.data} />
          ) : (
            <div className="loading-placeholder">No micronutrient records found.</div>
          )}
        </section>
      </div>
    </div>
  );
}
