import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import type { GoalTargetInput } from "../../api/contracts/goals";
import { ApiError } from "../../api/errors";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { Field } from "../../components/Field";
import { useToast } from "../../components/ToastProvider";
import { useProfileTimezone } from "../../hooks/useProfileTimezone";
import { localDateString } from "../../utils/zonedDateTime";
import { createGoal } from "./api";

type Values = {
  name: string;
  effectiveFrom: string;
  effectiveTo: string;
  targetWeightKg: number | string;
  calories: number;
  protein: number | string;
  carbs: number | string;
  fat: number | string;
};

function errorMessage(error: unknown): string {
  if (error instanceof ApiError && error.code === "GOAL_PERIOD_CONFLICT") {
    return "A goal already covers part of this date range. Choose a later start date or archive overlapping goals.";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Unable to save goal. Please check the values and try again.";
}

export function GoalForm({ onComplete }: { onComplete?(): void }): React.JSX.Element {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const timezone = useProfileTimezone();
  const [isOpen, setIsOpen] = useState(false);

  const form = useForm<Values>({
    defaultValues: {
      name: "Daily Nutrition Goal",
      effectiveFrom: localDateString(new Date(), timezone),
      effectiveTo: "",
      targetWeightKg: "",
      calories: 2000,
      protein: 120,
      carbs: 220,
      fat: 65,
    },
  });

  const mutation = useMutation({
    mutationFn: (values: Values) => {
      const targets: GoalTargetInput[] = [
        {
          nutrientCode: "ENERGY_KCAL",
          targetAmount: values.calories || 2000,
          targetKind: "TARGET",
        },
      ];

      const p = Number(values.protein);
      if (p > 0) {
        targets.push({
          nutrientCode: "PROTEIN",
          targetAmount: p,
          targetKind: "MINIMUM",
        });
      }

      const c = Number(values.carbs);
      if (c > 0) {
        targets.push({
          nutrientCode: "CARBOHYDRATE",
          targetAmount: c,
          targetKind: "TARGET",
        });
      }

      const f = Number(values.fat);
      if (f > 0) {
        targets.push({
          nutrientCode: "FAT",
          targetAmount: f,
          targetKind: "TARGET",
        });
      }

      const weight = values.targetWeightKg ? Number(values.targetWeightKg) : null;

      return createGoal({
        name: values.name.trim() || "Daily Nutrition Goal",
        effectiveFrom: values.effectiveFrom,
        effectiveTo: values.effectiveTo ? values.effectiveTo : null,
        targetWeightKg: weight && weight > 0 ? weight : null,
        targets,
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["goals"] });
      void queryClient.invalidateQueries({ queryKey: ["goal"] });
      void queryClient.invalidateQueries({ queryKey: ["reports"] });
      showToast("New health goal created successfully!", "success");
      setIsOpen(false);
      form.reset();
      onComplete?.();
    },
  });

  const submit = form.handleSubmit((values) => mutation.mutate(values));

  if (!isOpen) {
    return (
      <div className="card set-goal-banner">
        <div>
          <h3>Set a New Health & Nutrition Goal</h3>
          <p className="form-subtitle">
            Define daily calorie and macronutrient targets to monitor your progress on the dashboard.
          </p>
        </div>
        <Button variant="primary" onClick={() => setIsOpen(true)}>
          ➕ Create New Goal
        </Button>
      </div>
    );
  }

  return (
    <form className="card form-layout" onSubmit={(event) => void submit(event)}>
      <div className="form-header">
        <div className="form-header__title-row">
          <h2>Create New Health Goal</h2>
          <Button
            type="button"
            variant="ghost"
            size="small"
            onClick={() => setIsOpen(false)}
          >
            ✕ Close
          </Button>
        </div>
        <p className="form-subtitle">
          Setting a new goal automatically closes or archives your previous active goal.
        </p>
      </div>

      <div className="form-grid">
        <div className="form-col-span-2">
          <Field
            label="Goal Plan Name *"
            placeholder="e.g., Summer Cut, Muscle Building, Healthy Maintenance"
            required
            {...form.register("name", { required: true })}
          />
        </div>

        <Field
          label="Effective From *"
          type="date"
          required
          {...form.register("effectiveFrom", { required: true })}
        />

        <Field
          label="Effective To (optional)"
          type="date"
          {...form.register("effectiveTo")}
        />

        <Field
          label="Target Body Weight (kg, optional)"
          type="number"
          step="0.1"
          min="0"
          placeholder="e.g. 70.0"
          {...form.register("targetWeightKg")}
        />
      </div>

      <div className="macros-section">
        <h3 className="section-title">Daily Nutritional Targets</h3>
        <div className="macros-grid">
          <Field
            label="Energy (Calories, kcal) *"
            type="number"
            step="10"
            min="500"
            required
            {...form.register("calories", { valueAsNumber: true, required: true })}
          />
          <Field
            label="Protein Target (g)"
            type="number"
            step="1"
            min="0"
            {...form.register("protein")}
          />
          <Field
            label="Carbohydrate Target (g)"
            type="number"
            step="1"
            min="0"
            {...form.register("carbs")}
          />
          <Field
            label="Fat Target (g)"
            type="number"
            step="1"
            min="0"
            {...form.register("fat")}
          />
        </div>
      </div>

      {mutation.isError && <Alert>{errorMessage(mutation.error)}</Alert>}

      <div className="form-actions">
        <div className="form-actions__left" />
        <div className="form-actions__right">
          <Button
            type="button"
            variant="outline"
            onClick={() => setIsOpen(false)}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={mutation.isPending}
          >
            Save & Activate Goal
          </Button>
        </div>
      </div>
    </form>
  );
}
