import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";

import type { ExtractionResult } from "../../api/contracts/extractions";
import type { MealEntry, MealNutrientInput } from "../../api/contracts/meals";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { Field } from "../../components/Field";
import { useToast } from "../../components/ToastProvider";
import { useProfileTimezone } from "../../hooks/useProfileTimezone";
import { localDateTimeInput, offsetDateTime } from "../../utils/zonedDateTime";
import { deleteMeal, saveMeal } from "./api";

type Values = {
  foodName: string;
  mealType: "BREAKFAST" | "LUNCH" | "DINNER" | "SNACKS";
  quantity: number;
  unit: string;
  description: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  occurredAt: string;
  notes: string;
};

type Props = {
  meal?: MealEntry;
  extraction?: ExtractionResult;
  extractionId?: string;
  onSuccessRedirect?: string;
};

export function MealForm({
  meal,
  extraction,
  extractionId,
  onSuccessRedirect = "/meals",
}: Props): React.JSX.Element {
  const timezone = useProfileTimezone();
  const navigate = useNavigate();
  const queries = useQueryClient();
  const { showToast } = useToast();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const getNutrientAmount = (code: string, fallback = 0): number => {
    if (meal) {
      const found = meal.nutrients.find((n) => n.code === code);
      if (found) return found.amount;
    }
    if (extraction) {
      const found = extraction.nutrients.find((n) => n.code === code);
      if (found) return found.amount;
    }
    return fallback;
  };

  const form = useForm<Values>({
    defaultValues: {
      foodName: meal?.foodName ?? extraction?.foodName ?? "",
      mealType: meal?.mealType ?? extraction?.suggestedMealType ?? "LUNCH",
      quantity: meal?.quantity.value ?? extraction?.quantity.value ?? 1,
      unit: meal?.quantity.unit ?? extraction?.quantity.unit ?? "serving",
      description: meal?.quantity.description ?? extraction?.quantity.description ?? "",
      calories: getNutrientAmount("ENERGY_KCAL", 0),
      protein: getNutrientAmount("PROTEIN", 0),
      carbs: getNutrientAmount("CARBOHYDRATE", 0),
      fat: getNutrientAmount("FAT", 0),
      occurredAt: localDateTimeInput(meal?.occurredAt ?? new Date(), timezone),
      notes: meal?.notes ?? "",
    },
  });

  const saveMutation = useMutation({
    mutationFn: (values: Values) => {
      const nutrients: MealNutrientInput[] = [
        { code: "ENERGY_KCAL", amount: values.calories || 0 },
      ];

      if (values.protein > 0) {
        nutrients.push({ code: "PROTEIN", amount: values.protein });
      }
      if (values.carbs > 0) {
        nutrients.push({ code: "CARBOHYDRATE", amount: values.carbs });
      }
      if (values.fat > 0) {
        nutrients.push({ code: "FAT", amount: values.fat });
      }

      // Preserve any other extracted nutrients (like vitamins, minerals, fiber)
      if (extraction) {
        for (const ext of extraction.nutrients) {
          if (!["ENERGY_KCAL", "PROTEIN", "CARBOHYDRATE", "FAT"].includes(ext.code)) {
            nutrients.push({
              code: ext.code,
              amount: ext.amount,
              confidence: ext.confidence,
            });
          }
        }
      } else if (meal) {
        for (const existing of meal.nutrients) {
          if (!["ENERGY_KCAL", "PROTEIN", "CARBOHYDRATE", "FAT"].includes(existing.code)) {
            nutrients.push({
              code: existing.code,
              amount: existing.amount,
              confidence: existing.confidence ?? null,
            });
          }
        }
      }

      return saveMeal(
        {
          mealType: values.mealType,
          foodName: values.foodName.trim(),
          quantity: {
            value: values.quantity || 1,
            unit: values.unit.trim() || "serving",
            description: values.description.trim() || null,
          },
          occurredAt: offsetDateTime(values.occurredAt, timezone),
          timezone,
          source: extractionId ? "IMAGE" : meal?.source ?? "MANUAL",
          sourceExtractionId: extractionId ?? meal?.sourceExtractionId ?? null,
          notes: values.notes.trim() || null,
          nutrients,
        },
        meal?.id
      );
    },
    onSuccess: () => {
      void queries.invalidateQueries({ queryKey: ["meals"] });
      void queries.invalidateQueries({ queryKey: ["reports"] });
      void queries.invalidateQueries({ queryKey: ["goal"] });
      showToast(meal ? "Meal updated successfully!" : "Meal logged successfully!", "success");
      navigate(onSuccessRedirect);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => {
      if (!meal?.id) return Promise.reject(new Error("No meal ID"));
      return deleteMeal(meal.id);
    },
    onSuccess: () => {
      void queries.invalidateQueries({ queryKey: ["meals"] });
      void queries.invalidateQueries({ queryKey: ["reports"] });
      void queries.invalidateQueries({ queryKey: ["goal"] });
      showToast("Meal deleted", "info");
      navigate("/meals");
    },
  });

  const submit = form.handleSubmit((values) => saveMutation.mutate(values));

  return (
    <>
      <form className="card form-layout" onSubmit={(event) => void submit(event)}>
        <div className="form-header">
          <h2>{meal ? "Edit Meal" : extraction ? "Review & Log Meal" : "Log a Meal"}</h2>
          <p className="form-subtitle">
            {extraction
              ? "Verify the AI-extracted details below before saving to your diary."
              : "Enter the nutritional details for your food entry."}
          </p>
        </div>

        <div className="form-grid">
          <div className="form-col-span-2">
            <Field
              label="Food name *"
              placeholder="e.g., Grilled Chicken Salad, Oatmeal with Honey"
              required
              {...form.register("foodName", { required: true })}
            />
          </div>

          <label className="field">
            <span>Meal type *</span>
            <select {...form.register("mealType")}>
              <option value="BREAKFAST">🌅 Breakfast</option>
              <option value="LUNCH">☀️ Lunch</option>
              <option value="DINNER">🌙 Dinner</option>
              <option value="SNACKS">🍎 Snacks</option>
            </select>
          </label>

          <Field
            label={`When (${timezone}) *`}
            type="datetime-local"
            required
            {...form.register("occurredAt", { required: true })}
          />

          <div className="form-row">
            <Field
              label="Quantity *"
              type="number"
              step="0.01"
              min="0.01"
              required
              {...form.register("quantity", { valueAsNumber: true, required: true })}
            />
            <Field
              label="Unit *"
              placeholder="serving, bowl, plate, g"
              required
              {...form.register("unit", { required: true })}
            />
          </div>

          <Field
            label="Portion description (optional)"
            placeholder="e.g., 1 medium bowl, 2 slices"
            {...form.register("description")}
          />
        </div>

        <div className="macros-section">
          <h3 className="section-title">Nutritional Information</h3>
          <div className="macros-grid">
            <Field
              label="Calories (kcal) *"
              type="number"
              step="1"
              min="0"
              required
              {...form.register("calories", { valueAsNumber: true, required: true })}
            />
            <Field
              label="Protein (g)"
              type="number"
              step="0.1"
              min="0"
              {...form.register("protein", { valueAsNumber: true })}
            />
            <Field
              label="Carbohydrates (g)"
              type="number"
              step="0.1"
              min="0"
              {...form.register("carbs", { valueAsNumber: true })}
            />
            <Field
              label="Fat (g)"
              type="number"
              step="0.1"
              min="0"
              {...form.register("fat", { valueAsNumber: true })}
            />
          </div>
        </div>

        <Field
          label="Notes (optional)"
          placeholder="Any custom notes, restaurant name, recipe adjustments…"
          {...form.register("notes")}
        />

        {saveMutation.isError && (
          <Alert>
            Unable to save meal. Please verify that all required fields and valid amounts are provided.
          </Alert>
        )}

        <div className="form-actions">
          <div className="form-actions__left">
            {meal && (
              <Button
                type="button"
                variant="danger"
                onClick={() => setShowDeleteConfirm(true)}
                disabled={saveMutation.isPending || deleteMutation.isPending}
              >
                Delete Meal
              </Button>
            )}
          </div>
          <div className="form-actions__right">
            <Link to="/meals">
              <Button type="button" variant="outline">
                Cancel
              </Button>
            </Link>
            <Button
              type="submit"
              variant="primary"
              isLoading={saveMutation.isPending}
            >
              {meal ? "Update Meal" : "Save to Diary"}
            </Button>
          </div>
        </div>
      </form>

      {meal && (
        <ConfirmDialog
          open={showDeleteConfirm}
          title="Delete this meal?"
          description={`Are you sure you want to remove "${meal.foodName}" from your diary? This action cannot be undone.`}
          confirmLabel="Delete"
          variant="danger"
          isLoading={deleteMutation.isPending}
          onConfirm={() => deleteMutation.mutate()}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </>
  );
}
