import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Alert } from "../components/Alert";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { deleteGoal, getGoals } from "../features/goals/api";
import { GoalCard } from "../features/goals/GoalCard";
import { GoalForm } from "../features/goals/GoalForm";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function GoalsPage(): React.JSX.Element {
  useDocumentTitle("Goals");
  const goals = useQuery({ queryKey: ["goals"], queryFn: getGoals });
  const queryClient = useQueryClient();
  const archive = useMutation({
    mutationFn: deleteGoal,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["goals"] });
      void queryClient.invalidateQueries({ queryKey: ["goal", "current"] });
    },
  });

  return (
    <>
      <h1>Goals</h1>
      <GoalForm />
      {archive.isError && <Alert>Goal could not be archived. Please try again.</Alert>}
      {goals.isLoading ? (
        <LoadingState />
      ) : goals.data?.data.length ? (
        <div className="grid">
          {goals.data.data.map((goal) => (
            <GoalCard
              archiving={archive.isPending}
              goal={goal}
              key={goal.id}
              onArchive={(id) => archive.mutate(id)}
            />
          ))}
        </div>
      ) : (
        <EmptyState>No active goals. Create one above to see it on your dashboard.</EmptyState>
      )}
    </>
  );
}
