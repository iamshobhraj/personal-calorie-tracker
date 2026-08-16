import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import type { ProfileUpdateInput } from "../../api/contracts/profile";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { Field } from "../../components/Field";
import { LoadingState } from "../../components/LoadingState";
import { useToast } from "../../components/ToastProvider";
import { getProfile, updateProfile } from "./api";

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

export function ProfileForm(): React.JSX.Element {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [copiedId, setCopiedId] = useState(false);

  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: getProfile,
  });

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<ProfileUpdateInput>();

  const selectedTimezone = watch("timezone") || (profileQuery.data?.data.timezone ?? "UTC");

  const mutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: (res) => {
      void queryClient.invalidateQueries({ queryKey: ["profile"] });
      void queryClient.invalidateQueries({ queryKey: ["meals"] });
      void queryClient.invalidateQueries({ queryKey: ["goals"] });
      void queryClient.invalidateQueries({ queryKey: ["reports"] });
      showToast(`Profile updated! Timezone set to ${res.data.timezone}`, "success");
    },
  });

  if (profileQuery.isLoading) return <LoadingState />;
  if (profileQuery.isError || !profileQuery.data) {
    return <Alert>Profile could not be loaded. Please refresh the page.</Alert>;
  }

  const profile = profileQuery.data.data;
  const userInitials = (profile.displayName || "User")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .substring(0, 2)
    .toUpperCase();

  const handleAutoDetectTimezone = () => {
    try {
      const detected = Intl.DateTimeFormat().resolvedOptions().timeZone;
      setValue("timezone", detected, { shouldDirty: true });
      showToast(`Detected timezone: ${detected}`, "info");
    } catch {
      showToast("Could not detect local timezone.", "error");
    }
  };

  const handleCopyId = () => {
    void navigator.clipboard.writeText(profile.id);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
    showToast("User ID copied to clipboard", "info");
  };

  const onSubmit = handleSubmit((values) => {
    mutation.mutate({
      displayName: values.displayName.trim(),
      timezone: values.timezone.trim(),
    });
  });

  // Calculate live preview time in selected timezone
  let previewTime = "—";
  try {
    previewTime = new Intl.DateTimeFormat("en-US", {
      timeZone: selectedTimezone,
      dateStyle: "full",
      timeStyle: "medium",
    }).format(new Date());
  } catch {
    previewTime = "Invalid timezone format";
  }

  return (
    <div className="profile-container">
      {/* Hero Profile Card */}
      <section className="card profile-hero-card">
        <div className="profile-avatar-circle">{userInitials}</div>
        <div className="profile-hero-info">
          <h2 className="profile-hero-name">{profile.displayName || "Account User"}</h2>
          <p className="profile-hero-email">{profile.email || "demo-user@dailyplate.internal"}</p>
          <div className="profile-hero-badges">
            <span className="badge badge--plate">Standard Plan</span>
            <span className="badge badge--confidence">Zone: {profile.timezone}</span>
          </div>
        </div>
      </section>

      {/* Edit Settings Form Card */}
      <section className="card form-layout">
        <div className="form-header">
          <h3 className="section-title">Personal Settings & Timezone</h3>
          <p className="form-subtitle">
            Your timezone ensures meal entries, daily calorie budgets, and reports are grouped into the right calendar days.
          </p>
        </div>

        <form className="form-layout" onSubmit={(e) => void onSubmit(e)}>
          <div className="form-grid">
            <div className="form-col-span-2">
              <Field
                label="Display Name *"
                defaultValue={profile.displayName ?? ""}
                placeholder="e.g. Shobh Raj"
                {...register("displayName", { required: "Display name is required" })}
              />
              {errors.displayName && (
                <span className="warning-item">{errors.displayName.message}</span>
              )}
            </div>

            <div className="form-col-span-2">
              <div className="timezone-field-wrap">
                <label className="field">
                  <div className="timezone-label-row">
                    <span>IANA Timezone *</span>
                    <button
                      type="button"
                      className="link-sm"
                      onClick={handleAutoDetectTimezone}
                    >
                      ⚡ Auto-Detect Local Timezone
                    </button>
                  </div>
                  <input
                    list="common-timezones"
                    defaultValue={profile.timezone}
                    placeholder="e.g. Asia/Kolkata or America/New_York"
                    {...register("timezone", { required: "Timezone is required" })}
                  />
                  <datalist id="common-timezones">
                    {COMMON_TIMEZONES.map((tz) => (
                      <option key={tz} value={tz} />
                    ))}
                  </datalist>
                </label>
              </div>

              {/* Timezone Live Preview */}
              <div className="timezone-preview-pill">
                <span className="tz-preview-label">Current Wall Clock Time:</span>
                <strong className="tz-preview-value">🕒 {previewTime}</strong>
              </div>
            </div>
          </div>

          {mutation.isError && (
            <Alert>
              Could not save profile changes. Please verify that the IANA timezone is valid.
            </Alert>
          )}

          <div className="form-actions">
            <div className="form-actions__left">
              <span className="form-subtitle">Changes take effect immediately across all charts.</span>
            </div>
            <div className="form-actions__right">
              <Button
                type="submit"
                variant="primary"
                size="large"
                disabled={mutation.isPending}
                isLoading={mutation.isPending}
              >
                Save Changes
              </Button>
            </div>
          </div>
        </form>
      </section>

      {/* Account Info & Security Metadata */}
      <section className="card form-layout">
        <h3 className="section-title">Account & Tenant Details</h3>
        <div className="account-meta-grid">
          <div className="meta-item">
            <span className="meta-label">User Email</span>
            <span className="meta-value">{profile.email || "demo-user@dailyplate.internal"}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Tenant User ID</span>
            <div className="meta-id-row">
              <code className="meta-code">{profile.id}</code>
              <Button
                type="button"
                variant="outline"
                size="small"
                onClick={handleCopyId}
              >
                {copiedId ? "✓ Copied" : "Copy ID"}
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
