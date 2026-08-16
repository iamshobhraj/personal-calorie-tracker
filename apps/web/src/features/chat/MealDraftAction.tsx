import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import type { MealDraftAction as MealDraftActionType } from "../../api/contracts/chat";
import { Button } from "../../components/Button";
import { useToast } from "../../components/ToastProvider";
import { saveMeal } from "../meals/api";

export function MealDraftAction({
  action,
}: {
  action: MealDraftActionType;
}): React.JSX.Element {
  const [logged, setLogged] = useState(false);
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const draft = action.draft;

  const mutation = useMutation({
    mutationFn: () => saveMeal(draft, undefined, action.confirmationToken),
    onSuccess: () => {
      setLogged(true);
      void queryClient.invalidateQueries({ queryKey: ["meals"] });
      void queryClient.invalidateQueries({ queryKey: ["reports"] });
      void queryClient.invalidateQueries({ queryKey: ["goal"] });
      showToast(`Logged "${draft.foodName}" to your diary!`, "success");
    },
    onError: (err) => {
      showToast(err instanceof Error ? err.message : "Could not save meal. Please try logging manually.", "error");
    },
  });

  const calories = draft.nutrients.find((n) => n.code === "ENERGY_KCAL")?.amount;
  const protein = draft.nutrients.find((n) => n.code === "PROTEIN")?.amount;
  const carbs = draft.nutrients.find((n) => n.code === "CARBOHYDRATE")?.amount;
  const fat = draft.nutrients.find((n) => n.code === "FAT")?.amount;

  return (
    <div className="meal-draft-card card">
      <div className="meal-draft-card__top">
        <span className="meal-draft-card__badge">📝 Meal Suggestion</span>
        <span className="meal-draft-card__type">{draft.mealType}</span>
      </div>

      <h4 className="meal-draft-card__title">{draft.foodName}</h4>
      <p className="meal-draft-card__portion">
        {draft.quantity.value} {draft.quantity.unit}
        {draft.quantity.description ? ` (${draft.quantity.description})` : ""}
      </p>

      <div className="meal-draft-card__nutrients">
        {calories !== undefined && (
          <span className="draft-pill draft-pill--cal">{calories} kcal</span>
        )}
        {protein !== undefined && (
          <span className="draft-pill">{protein}g Protein</span>
        )}
        {carbs !== undefined && (
          <span className="draft-pill">{carbs}g Carbs</span>
        )}
        {fat !== undefined && (
          <span className="draft-pill">{fat}g Fat</span>
        )}
      </div>

      <div className="meal-draft-card__footer">
        {logged ? (
          <div className="meal-draft-card__logged-state">
            <span className="logged-check">✓ Added to your diary</span>
            <Link to="/meals" className="link-sm">
              View in Diary →
            </Link>
          </div>
        ) : (
          <Button
            type="button"
            variant="primary"
            size="small"
            isLoading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            ✓ Confirm & Log Meal
          </Button>
        )}
      </div>
    </div>
  );
}
