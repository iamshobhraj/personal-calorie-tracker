import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { CalorieTrendChart } from "../charts/CalorieTrendChart";
import { MacroChart } from "../charts/MacroChart";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { getCurrentGoal } from "../features/goals/api";
import { getMeals } from "../features/meals/api";
import { reports } from "../features/reports/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";


function GoalProgressBar({
  label,
  actual,
  target,
  unit,
  targetKind,
  colorClass = "progress--brand",
}: {
  label: string;
  actual: number;
  target: number;
  unit: string;
  targetKind: string;
  colorClass?: string;
}): React.JSX.Element {
  const percent = target > 0 ? Math.round((actual / target) * 100) : 0;
  const remaining = target - actual;

  let statusText = `${Math.abs(remaining)} ${unit} ${remaining >= 0 ? "remaining" : "over"}`;
  if (targetKind === "MINIMUM") {
    statusText = actual >= target ? "✓ Minimum reached" : `${Math.abs(remaining)} ${unit} to reach target`;
  }

  return (
    <div className="macro-progress-card">
      <div className="macro-progress__header">
        <span className="macro-progress__name">{label}</span>
        <span className="macro-progress__percentage">{percent}%</span>
      </div>
      <div className="macro-progress__bar-wrap">
        <div
          className={`macro-progress__fill ${colorClass}`}
          style={{ width: `${Math.min(percent, 100)}%` }}
        />
      </div>
      <div className="macro-progress__footer">
        <span className="macro-progress__numbers">
          <strong>{actual}</strong> / {target} {unit}
        </span>
        <span className="macro-progress__status">{statusText}</span>
      </div>
    </div>
  );
}

export function DashboardPage(): React.JSX.Element {
  useDocumentTitle("Dashboard");
  const today = new Date().toISOString().slice(0, 10);
  const query = `dateFrom=${today}&dateTo=${today}&interval=DAY&page=1&limit=20`;

  const goal = useQuery({ queryKey: ["goal", "current"], queryFn: getCurrentGoal });
  const meals = useQuery({
    queryKey: ["meals", today],
    queryFn: () => getMeals(`dateFrom=${today}&dateTo=${today}&page=1&limit=50`),
  });
  const calories = useQuery({
    queryKey: ["reports", "calories", query],
    queryFn: () => reports(query).calories,
  });
  const macros = useQuery({
    queryKey: ["reports", "macros", query],
    queryFn: () => reports(query).macros,
  });

  if (meals.isLoading) return <LoadingState />;

  const todayMeals = meals.data?.data ?? [];
  const nutrientTotals = new Map<string, number>();

  todayMeals.flatMap((meal) => meal.nutrients).forEach((nutrient) => {
    nutrientTotals.set(nutrient.code, (nutrientTotals.get(nutrient.code) ?? 0) + nutrient.amount);
  });

  const currentGoal = goal.data?.data;
  const calorieActual = nutrientTotals.get("ENERGY_KCAL") ?? 0;
  const calorieTarget = currentGoal?.targets.find((t) => t.nutrientCode === "ENERGY_KCAL")?.targetAmount;
  const calorieRemaining = calorieTarget !== undefined ? calorieTarget - calorieActual : undefined;

  const proteinActual = nutrientTotals.get("PROTEIN") ?? 0;
  const proteinTarget = currentGoal?.targets.find((t) => t.nutrientCode === "PROTEIN");

  const carbsActual = nutrientTotals.get("CARBOHYDRATE") ?? 0;
  const carbsTarget = currentGoal?.targets.find((t) => t.nutrientCode === "CARBOHYDRATE");

  const fatActual = nutrientTotals.get("FAT") ?? 0;
  const fatTarget = currentGoal?.targets.find((t) => t.nutrientCode === "FAT");

  return (
    <div className="page-container">
      {/* Header with Quick Actions */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Today's Nutrition</h1>
          <p className="page-subtitle">
            {new Date().toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" })}
          </p>
        </div>
        <div className="page-header__actions">
          <Link to="/analyze">
            <Button variant="outline">📸 Scan Food</Button>
          </Link>
          <Link to="/meals/new">
            <Button variant="primary">➕ Log Meal</Button>
          </Link>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="stats-hero-grid">
        {/* Calorie Card */}
        <Card className="calorie-hero-card">
          <span className="hero-card__badge">🔥 Energy Today</span>
          <div className="hero-card__main-stat">
            <span className="hero-stat-value">{calorieActual}</span>
            <span className="hero-stat-unit">kcal</span>
          </div>

          {calorieTarget !== undefined ? (
            <div className="hero-card__target-info">
              <div className="hero-progress-bar">
                <div
                  className="hero-progress-fill"
                  style={{ width: `${Math.min((calorieActual / calorieTarget) * 100, 100)}%` }}
                />
              </div>
              <div className="hero-card__target-details">
                <span>Goal: {calorieTarget} kcal</span>
                <strong>
                  {calorieRemaining !== undefined && calorieRemaining >= 0
                    ? `${calorieRemaining} kcal remaining`
                    : `${Math.abs(calorieRemaining ?? 0)} kcal over goal`}
                </strong>
              </div>
            </div>
          ) : (
            <div className="hero-card__target-info">
              <p className="hint-text">No active calorie target set.</p>
              <Link to="/goals">
                <Button size="small" variant="outline">
                  Set a Goal
                </Button>
              </Link>
            </div>
          )}
        </Card>

        {/* Daily Macros Card */}
        <Card className="macros-hero-card">
          <div className="macros-hero-header">
            <h3>Macronutrients</h3>
            {currentGoal ? (
              <span className="goal-name-pill">{currentGoal.name}</span>
            ) : (
              <Link to="/goals" className="link-sm">
                Set Targets →
              </Link>
            )}
          </div>

          <div className="macros-list">
            <GoalProgressBar
              label="Protein"
              actual={proteinActual}
              target={proteinTarget?.targetAmount ?? 100}
              unit="g"
              targetKind={proteinTarget?.targetKind ?? "TARGET"}
              colorClass="progress--protein"
            />
            <GoalProgressBar
              label="Carbs"
              actual={carbsActual}
              target={carbsTarget?.targetAmount ?? 200}
              unit="g"
              targetKind={carbsTarget?.targetKind ?? "TARGET"}
              colorClass="progress--carbs"
            />
            <GoalProgressBar
              label="Fat"
              actual={fatActual}
              target={fatTarget?.targetAmount ?? 60}
              unit="g"
              targetKind={fatTarget?.targetKind ?? "TARGET"}
              colorClass="progress--fat"
            />
          </div>
        </Card>
      </div>

      {/* Today's Meals Section */}
      <section className="dashboard-section">
        <div className="section-header">
          <h2 className="section-title">Today's Meals ({todayMeals.length})</h2>
          <Link to="/meals">
            <Button size="small" variant="ghost">
              View All in Diary →
            </Button>
          </Link>
        </div>

        {todayMeals.length > 0 ? (
          <div className="today-meals-grid">
            {todayMeals.map((meal) => {
              const cal = meal.nutrients.find((n) => n.code === "ENERGY_KCAL")?.amount ?? 0;
              return (
                <div key={meal.id} className="today-meal-chip card">
                  <div className="today-meal-chip__top">
                    <span className="today-meal-chip__type">{meal.mealType}</span>
                    <span className="today-meal-chip__cal">{cal} kcal</span>
                  </div>
                  <strong className="today-meal-chip__name">{meal.foodName}</strong>
                  <span className="today-meal-chip__qty">
                    {meal.quantity.value} {meal.quantity.unit}
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <EmptyState>
            <p>No meals logged yet today.</p>
            <div className="row justify-center">
              <Link to="/meals/new">
                <Button size="small" variant="primary">
                  Log Breakfast, Lunch, or Dinner
                </Button>
              </Link>
            </div>
          </EmptyState>
        )}
      </section>

      {/* Analytics Charts */}
      <section className="dashboard-charts-grid">
        {calories.data && (
          <div className="chart-wrapper card">
            <h3 className="chart-wrapper__title">Calorie Intake</h3>
            <CalorieTrendChart data={calories.data.data} />
          </div>
        )}
        {macros.data && (
          <div className="chart-wrapper card">
            <h3 className="chart-wrapper__title">Macro Distribution</h3>
            <MacroChart data={macros.data.data} />
          </div>
        )}
      </section>
    </div>
  );
}
