import { Link, Navigate } from "react-router-dom";
import { AuthLayout } from "../features/auth/AuthLayout";
import { SignupForm } from "../features/auth/SignupForm";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useAuth } from "../state/auth/AuthContext";

export function SignupPage(): React.JSX.Element {
  useDocumentTitle("Create Account • Daily Plate");
  const { state } = useAuth();

  if (state.status === "authenticated") {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <AuthLayout
      activeTab="signup"
      title="Create your account"
      subtitle="Start tracking calories, macro targets, and nutrition insights today."
      footerPrompt={
        <p className="auth-switch-text">
          Already have an account?{" "}
          <Link to="/login" className="auth-switch-link">
            Sign in
          </Link>
        </p>
      }
    >
      <SignupForm />
    </AuthLayout>
  );
}
