import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";

import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { Field } from "../../components/Field";
import { useAuth } from "../../state/auth/AuthContext";
import { loginInputSchema } from "./schemas";

type Values = {
  email: string;
  password: string;
};

export function LoginForm(): React.JSX.Element {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);

  const form = useForm<Values>({
    resolver: zodResolver(loginInputSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const submit = form.handleSubmit(async (values) => {
    try {
      await login(values);
      navigate("/dashboard");
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Invalid email or password. Please check your credentials and try again.";
      form.setError("root", {
        message: msg,
      });
    }
  });

  return (
    <form className="auth-form" onSubmit={(e) => void submit(e)} noValidate>
      <div className="auth-form__fields">
        <Field
          label="Email address"
          type="email"
          autoComplete="email"
          placeholder="name@example.com"
          error={form.formState.errors.email?.message}
          {...form.register("email")}
        />

        <div className="password-field-wrap">
          <Field
            label="Password"
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            placeholder="Enter your password"
            error={form.formState.errors.password?.message}
            {...form.register("password")}
          />
          <button
            type="button"
            className="password-toggle-btn"
            onClick={() => setShowPassword((prev) => !prev)}
            aria-label={showPassword ? "Hide password" : "Show password"}
            tabIndex={-1}
          >
            {showPassword ? "🙈 Hide" : "👁️ Show"}
          </button>
        </div>
      </div>

      {form.formState.errors.root && (
        <Alert>{form.formState.errors.root.message}</Alert>
      )}

      <Button
        type="submit"
        variant="primary"
        size="large"
        className="btn--full"
        isLoading={form.formState.isSubmitting}
        disabled={form.formState.isSubmitting}
      >
        Sign in to Daily Plate
      </Button>
    </form>
  );
}
