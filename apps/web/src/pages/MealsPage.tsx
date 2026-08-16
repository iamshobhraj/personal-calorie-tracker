import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { Button } from "../components/Button";
import { LoadingState } from "../components/LoadingState";
import { MealFilters } from "../features/meals/MealFilters";
import { MealTable } from "../features/meals/MealTable";
import { getMeals } from "../features/meals/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useProfileTimezone } from "../hooks/useProfileTimezone";
import { localDateString } from "../utils/zonedDateTime";

export function MealsPage(): React.JSX.Element {
  useDocumentTitle("Meal Diary");
  const timezone = useProfileTimezone();
  const [params, setParams] = useSearchParams();
  const today = localDateString(new Date(), timezone);
  const from = params.get("dateFrom") ?? today;
  const to = params.get("dateTo") ?? today;

  const query = useQuery({
    queryKey: ["meals", from, to],
    queryFn: () => getMeals(`dateFrom=${from}&dateTo=${to}&page=1&limit=50`),
  });

  const handleRangeChange = (newFrom: string, newTo: string) => {
    setParams({ dateFrom: newFrom, dateTo: newTo });
  };

  const meals = query.data?.data ?? [];
  const totalCalories = meals.reduce((sum, meal) => {
    const cal = meal.nutrients.find((n) => n.code === "ENERGY_KCAL")?.amount ?? 0;
    return sum + cal;
  }, 0);

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Meal Diary</h1>
          <p className="page-subtitle">Track and review your logged foods and nutritional intake.</p>
        </div>
        <div className="page-header__actions">
          <Link to="/analyze">
            <Button variant="outline">📸 Scan Food / Label</Button>
          </Link>
          <Link to="/meals/new">
            <Button variant="primary">➕ Log New Meal</Button>
          </Link>
        </div>
      </div>

      <MealFilters
        dateFrom={from}
        dateTo={to}
        onDateFrom={(val) => setParams({ dateFrom: val, dateTo: to })}
        onDateTo={(val) => setParams({ dateFrom: from, dateTo: val })}
        onRangeChange={handleRangeChange}
      />

      {meals.length > 0 && (
        <div className="summary-bar card">
          <div className="summary-stat">
            <span className="summary-stat__label">Total Logged Meals</span>
            <strong className="summary-stat__value">{meals.length}</strong>
          </div>
          <div className="summary-stat">
            <span className="summary-stat__label">Total Energy</span>
            <strong className="summary-stat__value">{totalCalories} kcal</strong>
          </div>
        </div>
      )}

      {query.isLoading ? (
        <LoadingState />
      ) : (
        <MealTable meals={meals} />
      )}
    </div>
  );
}
