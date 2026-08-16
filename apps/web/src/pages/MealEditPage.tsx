import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { MealForm } from "../features/meals/MealForm";
import { getMeal } from "../features/meals/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function MealEditPage(): React.JSX.Element {
  const { mealEntryId = "" } = useParams();
  useDocumentTitle("Edit Meal");

  const query = useQuery({
    queryKey: ["meal", mealEntryId],
    queryFn: () => getMeal(mealEntryId),
    enabled: Boolean(mealEntryId),
  });

  return (
    <div className="page-container page-container--narrow">
      <nav className="breadcrumbs" aria-label="Breadcrumb">
        <Link to="/meals">← Back to Meal Diary</Link>
      </nav>

      {query.isLoading ? (
        <LoadingState />
      ) : query.data ? (
        <MealForm meal={query.data.data} />
      ) : (
        <EmptyState>
          <p>Meal entry not found or has been deleted.</p>
          <Link to="/meals">Back to Diary</Link>
        </EmptyState>
      )}
    </div>
  );
}
