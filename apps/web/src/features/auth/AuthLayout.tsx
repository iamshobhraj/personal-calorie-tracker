import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Card } from "../../components/Card";

export interface AuthLayoutProps {
  activeTab: "login" | "signup";
  title: string;
  subtitle: string;
  children: ReactNode;
  footerPrompt: ReactNode;
}

export function AuthLayout({
  activeTab,
  title,
  subtitle,
  children,
  footerPrompt,
}: AuthLayoutProps): React.JSX.Element {
  return (
    <div className="auth-layout">
      <div className="auth-container">
        {/* Brand Header */}
        <div className="auth-brand-wrap">
          <Link to="/" className="brand" aria-label="Daily Plate Home">
            <span className="brand__logo">🥑</span>
            <span className="brand__text">Daily Plate</span>
          </Link>
          <span className="auth-tagline">Personal Calorie & Nutrition Tracker</span>
        </div>

        {/* Main Auth Card */}
        <Card className="auth-card">
          {/* Segmented Navigation Tabs */}
          <nav className="auth-nav-tabs" aria-label="Authentication navigation">
            <Link
              to="/login"
              className={`auth-tab ${activeTab === "login" ? "auth-tab--active" : ""}`}
              aria-current={activeTab === "login" ? "page" : undefined}
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className={`auth-tab ${activeTab === "signup" ? "auth-tab--active" : ""}`}
              aria-current={activeTab === "signup" ? "page" : undefined}
            >
              Create Account
            </Link>
          </nav>

          {/* Page Heading */}
          <div className="auth-header">
            <h1 className="auth-title">{title}</h1>
            <p className="auth-subtitle">{subtitle}</p>
          </div>

          {/* Form Body */}
          <div className="auth-form-body">
            {children}
          </div>

          {/* Footer prompt */}
          <div className="auth-footer-prompt">
            {footerPrompt}
          </div>
        </Card>

        {/* Security & Privacy note */}
        <footer className="auth-footer">
          <span>🔒 End-to-end authenticated & private nutrition tracking</span>
        </footer>
      </div>
    </div>
  );
}
