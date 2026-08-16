import { Link } from "react-router-dom";
import { MealForm } from "../features/meals/MealForm";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function MealCreatePage(): React.JSX.Element {
  useDocumentTitle("Log New Meal");
  return (
    <div className="page-container page-container--narrow">
      <nav className="breadcrumbs" aria-label="Breadcrumb">
        <Link to="/meals">← Back to Meal Diary</Link>
      </nav>
      <MealForm />
    </div>
  );
}
