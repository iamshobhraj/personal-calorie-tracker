import { ProfileForm } from "../features/profile/ProfileForm";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function ProfilePage(): React.JSX.Element {
  useDocumentTitle("Profile & Preferences");

  return (
    <div className="page-container page-container--narrow">
      <div className="page-header">
        <div>
          <h1 className="page-title">Profile & Settings</h1>
          <p className="page-subtitle">
            Manage your personal display name, timezone rules, and calorie tracker preferences.
          </p>
        </div>
      </div>

      <ProfileForm />
    </div>
  );
}
