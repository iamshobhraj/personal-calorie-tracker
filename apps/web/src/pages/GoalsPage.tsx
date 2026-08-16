import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Alert } from "../components/Alert";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { useToast } from "../components/ToastProvider";
import { GoalCard } from "../features/goals/GoalCard";
import { GoalForm } from "../features/goals/GoalForm";
import { deleteGoal, getGoals } from "../features/goals/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function GoalsPage(): React.JSX.Element {
  useDocumentTitle("Health Goals");
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const goals = useQuery({ queryKey: ["goals"], queryFn: getGoals });

  const archiveMutation = useMutation({
    mutationFn: deleteGoal,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["goals"] });
      void queryClient.invalidateQueries({ queryKey: ["goal"] });
      void queryClient.invalidateQueries({ queryKey: ["reports"] });
      showToast("Goal archived successfully", "info");
    },
    onError: () => {
      showToast("Could not archive goal. Please try again.", "error");
    },
  });

  const activeGoals = goals.data?.data.filter((g) => g.status === "ACTIVE") ?? [];

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Health Goals</h1>
          <p className="page-subtitle">
            Set and manage your daily energy, macronutrient, and target weight objectives.
          </p>
        </div>
      </div>

      <GoalForm />

      <section className="goals-section">
        <h2 className="section-title">Active Goals</h2>
        {archiveMutation.isError && (
          <Alert>Goal could not be archived. Please try again.</Alert>
        )}

        {goals.isLoading ? (
          <LoadingState />
        ) : activeGoals.length > 0 ? (
          <div className="goals-grid">
            {activeGoals.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                archiving={archiveMutation.isPending}
                onArchive={(id) => archiveMutation.mutate(id)}
              />
            ))}
          </div>
        ) : (
          <EmptyState>
            <div className="empty-content">
              <p className="empty-title">No active goal found.</p>
              <p className="empty-subtitle">
                Create a daily calorie and macro target above to track your progress on the dashboard.
              </p>
            </div>
          </EmptyState>
        )}
      </section>
    </div>
  );
}
