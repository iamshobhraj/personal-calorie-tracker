import { createBrowserRouter, Navigate } from "react-router-dom";
import { NotFoundPage } from "../pages/NotFoundPage";
import { LoginPage } from "../pages/LoginPage";
import { SignupPage } from "../pages/SignupPage";
import { DashboardPage } from "../pages/DashboardPage";
import { MealsPage } from "../pages/MealsPage";
import { MealCreatePage } from "../pages/MealCreatePage";
import { MealEditPage } from "../pages/MealEditPage";
import { GoalsPage } from "../pages/GoalsPage";
import { AnalyzeImagePage } from "../pages/AnalyzeImagePage";
import { ReportsPage } from "../pages/ReportsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { ProtectedRoute } from "../state/auth/ProtectedRoute";
import { AppShell } from "./AppShell";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/signup", element: <SignupPage /> },
  { element: <ProtectedRoute />, children: [{ element: <AppShell />, children: [
    { path: "/", element: <Navigate to="/dashboard" replace /> }, { path: "/dashboard", element: <DashboardPage /> }, { path: "/meals", element: <MealsPage /> }, { path: "/meals/new", element: <MealCreatePage /> }, { path: "/meals/:mealEntryId/edit", element: <MealEditPage /> }, { path: "/goals", element: <GoalsPage /> }, { path: "/analyze", element: <AnalyzeImagePage /> }, { path: "/reports", element: <ReportsPage /> }, { path: "/profile", element: <ProfilePage /> },
  ] }] },
  { path: "*", element: <NotFoundPage /> },
]);
