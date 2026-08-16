import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import type { NutrientCode } from "../../api/contracts/common";
import { ApiError } from "../../api/errors";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { Field } from "../../components/Field";
import { getNutrients } from "../nutrition/api";

import { createGoal } from "./api";

type Values = {
  name: string;
  effectiveFrom: string;
  effectiveTo: string;
  targetAmount: number;
  nutrientCode: NutrientCode;
};

function errorMessage(error: unknown): string {
  if (error instanceof ApiError && error.code === "GOAL_PERIOD_CONFLICT") {
    return "This goal overlaps an active goal. Choose a start after its end, or archive the active goal first.";
  }

  return "Goal could not be saved. Check its date range.";
}

export function GoalForm(): React.JSX.Element {
  const nutrients = useQuery({ queryKey: ["nutrients"], queryFn: getNutrients });
  const queryClient = useQueryClient();
  const form = useForm<Values>({
    defaultValues: {
      name: "Daily goal",
      effectiveFrom: new Date().toISOString().slice(0, 10),
      nutrientCode: "ENERGY_KCAL",
      targetAmount: 2000,
    },
  });
  const mutation = useMutation({
    mutationFn: createGoal,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["goals"] });
      void queryClient.invalidateQueries({ queryKey: ["goal", "current"] });
    },
  });
  const submit = form.handleSubmit((values) =>
    mutation.mutate({
      name: values.name,
      effectiveFrom: values.effectiveFrom,
      effectiveTo: values.effectiveTo || null,
      targets: [
        {
          nutrientCode: values.nutrientCode,
          targetAmount: values.targetAmount,
          targetKind: "TARGET",
        },
      ],
    }),
  );

  return (
    <form
      className="card"
      onSubmit={(event) => {
        void submit(event);
      }}
    >
      <h2>New goal</h2>
      <Field label="Name" {...form.register("name")} />
      <Field label="Effective from" type="date" {...form.register("effectiveFrom")} />
      <Field label="Effective to" type="date" {...form.register("effectiveTo")} />
      <label className="field">
        <span>Nutrient</span>
        <select {...form.register("nutrientCode")}>
          {nutrients.data?.data.map((nutrient) => (
            <option key={nutrient.code} value={nutrient.code}>
              {nutrient.name} ({nutrient.unit})
            </option>
          ))}
        </select>
      </label>
      <Field
        label="Target amount"
        type="number"
        step="0.01"
        {...form.register("targetAmount", { valueAsNumber: true })}
      />
      {mutation.isError && <Alert>{errorMessage(mutation.error)}</Alert>}
      {mutation.isSuccess && <p role="status">Goal saved.</p>}
      <Button disabled={mutation.isPending}>Save goal</Button>
    </form>
  );
}
