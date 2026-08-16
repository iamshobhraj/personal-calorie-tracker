import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";

import type { ExtractionResult } from "../../api/contracts/extractions";
import type { MealEntry } from "../../api/contracts/meals";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { Field } from "../../components/Field";
import { useProfileTimezone } from "../../hooks/useProfileTimezone";
import { localDateTimeInput, offsetDateTime } from "../../utils/zonedDateTime";
import { saveMeal } from "./api";

type Values = {
  foodName: string;
  mealType: "BREAKFAST" | "LUNCH" | "DINNER" | "SNACKS";
  quantity: number;
  unit: string;
  calories: number;
  occurredAt: string;
  notes: string;
};

type Props = {
  meal?: MealEntry;
  extraction?: ExtractionResult;
  extractionId?: string;
};

export function MealForm({ meal, extraction, extractionId }: Props): React.JSX.Element {
  const timezone = useProfileTimezone();
  const navigate = useNavigate();
  const queries = useQueryClient();
  const form = useForm<Values>({
    defaultValues: {
      foodName: meal?.foodName ?? extraction?.foodName ?? "",
      mealType: meal?.mealType ?? extraction?.suggestedMealType ?? "LUNCH",
      quantity: meal?.quantity.value ?? extraction?.quantity.value ?? 1,
      unit: meal?.quantity.unit ?? extraction?.quantity.unit ?? "serving",
      calories:
        meal?.nutrients.find((nutrient) => nutrient.code === "ENERGY_KCAL")?.amount ??
        extraction?.nutrients.find((nutrient) => nutrient.code === "ENERGY_KCAL")?.amount ??
        0,
      occurredAt: localDateTimeInput(meal?.occurredAt ?? new Date(), timezone),
      notes: meal?.notes ?? "",
    },
  });
  const mutation = useMutation({
    mutationFn: (values: Values) => {
      const nutrients = extraction
        ? extraction.nutrients.map((nutrient) => ({
            code: nutrient.code,
            amount: nutrient.code === "ENERGY_KCAL" ? values.calories : nutrient.amount,
            confidence: nutrient.confidence,
          }))
        : [{ code: "ENERGY_KCAL" as const, amount: values.calories }];
      return saveMeal(
        {
          mealType: values.mealType,
          foodName: values.foodName,
          quantity: {
            value: values.quantity,
            unit: values.unit,
            description: extraction?.quantity.description ?? null,
          },
          occurredAt: offsetDateTime(values.occurredAt, timezone),
          timezone,
          source: extractionId ? "IMAGE" : "MANUAL",
          sourceExtractionId: extractionId ?? null,
          notes: values.notes || null,
          nutrients,
        },
        meal?.id,
      );
    },
    onSuccess: (result) => {
      void queries.invalidateQueries({ queryKey: ["meals"] });
      navigate(`/meals/${result.data.id}/edit`);
    },
  });
  const submit = form.handleSubmit((values) => mutation.mutate(values));

  return (
    <form className="card" onSubmit={(event) => void submit(event)}>
      <Field label="Food name" {...form.register("foodName")} />
      <label className="field">
        <span>Meal type</span>
        <select {...form.register("mealType")}>
          <option>BREAKFAST</option>
          <option>LUNCH</option>
          <option>DINNER</option>
          <option>SNACKS</option>
        </select>
      </label>
      <Field
        label="Quantity"
        type="number"
        step="0.01"
        {...form.register("quantity", { valueAsNumber: true })}
      />
      <Field label="Unit" {...form.register("unit")} />
      <Field
        label="Calories (kcal)"
        type="number"
        {...form.register("calories", { valueAsNumber: true })}
      />
      <Field label={`When (${timezone})`} type="datetime-local" {...form.register("occurredAt")} />
      <Field label="Notes" {...form.register("notes")} />
      {mutation.isError && <Alert>Meal could not be saved. Check the time, timezone, and nutrients.</Alert>}
      {mutation.isSuccess && <p role="status">Meal saved.</p>}
      <Button disabled={mutation.isPending}>Save meal</Button>
    </form>
  );
}
