import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import type { MealEntry } from "../../api/contracts/meals";
import { Button } from "../../components/Button";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { EmptyState } from "../../components/EmptyState";
import { useToast } from "../../components/ToastProvider";
import { deleteMeal } from "./api";

function formatMealType(type: string): { label: string; icon: string; className: string } {
  switch (type) {
    case "BREAKFAST":
      return { label: "Breakfast", icon: "🌅", className: "badge--breakfast" };
    case "LUNCH":
      return { label: "Lunch", icon: "☀️", className: "badge--lunch" };
    case "DINNER":
      return { label: "Dinner", icon: "🌙", className: "badge--dinner" };
    case "SNACKS":
      return { label: "Snacks", icon: "🍎", className: "badge--snacks" };
    default:
      return { label: type, icon: "🍴", className: "badge--default" };
  }
}

export function MealTable({ meals }: { meals: MealEntry[] }): React.JSX.Element {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [mealToDelete, setMealToDelete] = useState<MealEntry | null>(null);

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteMeal(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["meals"] });
      void queryClient.invalidateQueries({ queryKey: ["reports"] });
      void queryClient.invalidateQueries({ queryKey: ["goal"] });
      showToast("Meal deleted successfully", "info");
      setMealToDelete(null);
    },
    onError: () => {
      showToast("Failed to delete meal. Please try again.", "error");
    },
  });

  if (meals.length === 0) {
    return (
      <EmptyState>
        <div className="empty-content">
          <p className="empty-title">No meals found for this date range.</p>
          <p className="empty-subtitle">
            Log your breakfast, lunch, dinner, or snacks to track your nutrition progress.
          </p>
          <Link to="/meals/new">
            <Button variant="primary">Log a Meal</Button>
          </Link>
        </div>
      </EmptyState>
    );
  }

  return (
    <>
      <div className="meal-list">
        {meals.map((meal) => {
          const typeInfo = formatMealType(meal.mealType);
          const calories = meal.nutrients.find((n) => n.code === "ENERGY_KCAL")?.amount;
          const protein = meal.nutrients.find((n) => n.code === "PROTEIN")?.amount;
          const carbs = meal.nutrients.find((n) => n.code === "CARBOHYDRATE")?.amount;
          const fat = meal.nutrients.find((n) => n.code === "FAT")?.amount;

          return (
            <article key={meal.id} className="meal-card card">
              <div className="meal-card__header">
                <div className="meal-card__type">
                  <span className={`meal-badge ${typeInfo.className}`}>
                    {typeInfo.icon} {typeInfo.label}
                  </span>
                  <span className="meal-card__date">
                    {meal.localDate} • {new Date(meal.occurredAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
                <div className="meal-card__actions">
                  <Link to={`/meals/${meal.id}/edit`}>
                    <Button variant="outline" size="small">
                      Edit
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    size="small"
                    className="btn--danger-ghost"
                    onClick={() => setMealToDelete(meal)}
                  >
                    Delete
                  </Button>
                </div>
              </div>

              <div className="meal-card__body">
                <div className="meal-card__info">
                  <h3 className="meal-card__title">{meal.foodName}</h3>
                  <p className="meal-card__quantity">
                    {meal.quantity.value} {meal.quantity.unit}
                    {meal.quantity.description ? ` (${meal.quantity.description})` : ""}
                  </p>
                  {meal.notes && <p className="meal-card__notes">{meal.notes}</p>}
                </div>

                <div className="meal-card__nutrients">
                  <div className="nutrient-pill nutrient-pill--calories">
                    <span className="nutrient-pill__value">{calories !== undefined ? `${calories}` : "—"}</span>
                    <span className="nutrient-pill__label">kcal</span>
                  </div>
                  {protein !== undefined && (
                    <div className="nutrient-pill">
                      <span className="nutrient-pill__value">{protein}g</span>
                      <span className="nutrient-pill__label">Protein</span>
                    </div>
                  )}
                  {carbs !== undefined && (
                    <div className="nutrient-pill">
                      <span className="nutrient-pill__value">{carbs}g</span>
                      <span className="nutrient-pill__label">Carbs</span>
                    </div>
                  )}
                  {fat !== undefined && (
                    <div className="nutrient-pill">
                      <span className="nutrient-pill__value">{fat}g</span>
                      <span className="nutrient-pill__label">Fat</span>
                    </div>
                  )}
                </div>
              </div>
            </article>
          );
        })}
      </div>

      <ConfirmDialog
        open={mealToDelete !== null}
        title="Delete meal?"
        description={
          mealToDelete
            ? `Are you sure you want to delete "${mealToDelete.foodName}" (${mealToDelete.localDate}) from your diary?`
            : ""
        }
        confirmLabel="Delete"
        variant="danger"
        isLoading={deleteMutation.isPending}
        onConfirm={() => mealToDelete && deleteMutation.mutate(mealToDelete.id)}
        onCancel={() => setMealToDelete(null)}
      />
    </>
  );
}
