import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";

import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { Field } from "../../components/Field";
import { useAuth } from "../../state/auth/AuthContext";
import { signupInputSchema } from "./schemas";

const COMMON_TIMEZONES = [
  "Asia/Kolkata",
  "Asia/Dubai",
  "Asia/Singapore",
  "Asia/Tokyo",
  "Asia/Shanghai",
  "Europe/London",
  "Europe/Paris",
  "Europe/Berlin",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "America/Toronto",
  "Australia/Sydney",
  "UTC",
];

type Values = {
  email: string;
  password: string;
  displayName: string;
  timezone: string;
};

export function SignupForm(): React.JSX.Element {
  const { signup, login } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);

  const form = useForm<Values>({
    resolver: zodResolver(signupInputSchema),
    defaultValues: {
      displayName: "",
      email: "",
      password: "",
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
    },
  });

  const selectedTimezone = form.watch("timezone") || "UTC";

  const handleAutoDetectTimezone = () => {
    try {
      const detected = Intl.DateTimeFormat().resolvedOptions().timeZone;
      form.setValue("timezone", detected, { shouldDirty: true, shouldValidate: true });
    } catch {
      // Keep existing
    }
  };

  const submit = form.handleSubmit(async (values) => {
    try {
      await signup(values);
      await login({ email: values.email, password: values.password });
      navigate("/dashboard");
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "We could not create this account. Please try again.";
      form.setError("root", {
        message: msg,
      });
    }
  });

  let previewTime = "—";
  try {
    previewTime = new Intl.DateTimeFormat("en-US", {
      timeZone: selectedTimezone,
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date());
  } catch {
    previewTime = "Invalid timezone format";
  }

  return (
    <form className="auth-form" onSubmit={(e) => void submit(e)} noValidate>
      <div className="auth-form__fields">
        <Field
          label="Your name"
          type="text"
          autoComplete="name"
          placeholder="e.g. Alex Morgan"
          error={form.formState.errors.displayName?.message}
          {...form.register("displayName")}
        />

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
            label="Password (12+ characters)"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="At least 12 characters"
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

        <div className="timezone-field-wrap">
          <label className="field">
            <div className="timezone-label-row">
              <span>Timezone</span>
              <button
                type="button"
                className="link-sm"
                onClick={handleAutoDetectTimezone}
              >
                ⚡ Auto-Detect
              </button>
            </div>
            <input
              list="signup-common-timezones"
              placeholder="e.g. Asia/Kolkata or America/New_York"
              {...form.register("timezone")}
            />
            <datalist id="signup-common-timezones">
              {COMMON_TIMEZONES.map((tz) => (
                <option key={tz} value={tz} />
              ))}
            </datalist>
            {form.formState.errors.timezone && (
              <small role="alert">{form.formState.errors.timezone.message}</small>
            )}
          </label>

          <div className="timezone-preview-pill">
            <span className="tz-preview-label">Local preview:</span>
            <strong className="tz-preview-value">🕒 {previewTime}</strong>
          </div>
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
        Create Free Account
      </Button>
    </form>
  );
}
