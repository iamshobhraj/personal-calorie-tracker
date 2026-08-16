import { useQuery } from "@tanstack/react-query";

import { CalorieTrendChart } from "../charts/CalorieTrendChart";
import { MacroChart } from "../charts/MacroChart";
import { Card } from "../components/Card";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { Stat } from "../components/Stat";
import { getCurrentGoal } from "../features/goals/api";
import { getMeals } from "../features/meals/api";
import { reports } from "../features/reports/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

function nutrientLabel(code: string): string {
  return code.replaceAll("_", " ").toLowerCase().replace(/^\w/, (letter) => letter.toUpperCase());
}

function GoalProgress({
  actual,
  target,
  unit,
  targetKind,
}: {
  actual: number | undefined;
  target: number;
  unit: string;
  targetKind: string;
}): React.JSX.Element {
  if (actual === undefined) {
    return <p className="goal-progress__unknown">No meal data for this nutrient today.</p>;
  }

  const percent = target === 0 ? 0 : Math.round((actual / target) * 100);
  const difference = Math.abs(actual - target);
  const relationship =
    targetKind === "MINIMUM"
      ? actual >= target
        ? "minimum reached"
        : `${difference} ${unit} remaining`
      : targetKind === "MAXIMUM"
        ? actual <= target
          ? `${difference} ${unit} remaining`
          : `${difference} ${unit} over`
        : actual <= target
          ? `${difference} ${unit} remaining`
          : `${difference} ${unit} over`;

  return (
    <div className="goal-progress">
      <div className="goal-progress__numbers">
        <strong>
          {actual} / {target} {unit}
        </strong>
        <span>{percent}%</span>
      </div>
      <progress aria-label="Goal progress" max={Math.max(target, 1)} value={Math.min(actual, target)} />
      <p>{relationship}</p>
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
    queryFn: () => getMeals(`dateFrom=${today}&dateTo=${today}&page=1&limit=20`),
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

  const nutrientTotals = new Map<string, number>();
  meals.data?.data.flatMap((meal) => meal.nutrients).forEach((nutrient) => {
    nutrientTotals.set(nutrient.code, (nutrientTotals.get(nutrient.code) ?? 0) + nutrient.amount);
  });
  const calorieTotal = nutrientTotals.get("ENERGY_KCAL");

  return (
    <>
      <h1>Today</h1>
      <div className="grid">
        <Card>
          <Stat label="Calories" value={calorieTotal === undefined ? "Unknown" : `${calorieTotal} kcal`} />
        </Card>
        <Card>
          {goal.data ? (
            <>
              <div className="stat">
                <span>Current goal</span>
                <strong>{goal.data.data.name}</strong>
              </div>
              {goal.data.data.targets.map((target) => (
                <section className="goal-target" key={target.nutrientCode}>
                  <h2>{nutrientLabel(target.nutrientCode)}</h2>
                  <GoalProgress
                    actual={nutrientTotals.get(target.nutrientCode)}
                    target={target.targetAmount}
                    targetKind={target.targetKind}
                    unit={target.unit}
                  />
                </section>
              ))}
            </>
          ) : (
            <Stat label="Current goal" value="No goal yet" />
          )}
        </Card>
      </div>
      {goal.isError && <EmptyState>Create a goal to see progress.</EmptyState>}
      <section className="grid">
        {calories.data && <CalorieTrendChart data={calories.data.data} />}
        {macros.data && <MacroChart data={macros.data.data} />}
      </section>
    </>
  );
}
