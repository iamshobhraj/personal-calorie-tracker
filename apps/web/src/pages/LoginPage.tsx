import { Link, Navigate } from "react-router-dom";
import { AuthLayout } from "../features/auth/AuthLayout";
import { LoginForm } from "../features/auth/LoginForm";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useAuth } from "../state/auth/AuthContext";

export function LoginPage(): React.JSX.Element {
  useDocumentTitle("Sign In • Daily Plate");
  const { state } = useAuth();

  if (state.status === "authenticated") {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <AuthLayout
      activeTab="login"
      title="Welcome back"
      subtitle="Sign in with your email and password to continue tracking your meals."
      footerPrompt={
        <p className="auth-switch-text">
          Don't have an account?{" "}
          <Link to="/signup" className="auth-switch-link">
            Create an account
          </Link>
        </p>
      }
    >
      <LoginForm />
    </AuthLayout>
  );
}
