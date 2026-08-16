import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { Button } from "../components/Button";
import { SkipLink } from "../components/SkipLink";
import { useAuth } from "../state/auth/AuthContext";

const navLinks = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/meals", label: "Meals", icon: "🍽️" },
  { to: "/goals", label: "Goals", icon: "🎯" },
  { to: "/analyze", label: "AI Scan", icon: "📸" },
  { to: "/reports", label: "Reports", icon: "📈" },
  { to: "/chat", label: "AI Assistant", icon: "💬" },
  { to: "/imports", label: "PDF Import", icon: "📄" },
] as const;

export function AppShell(): React.JSX.Element {
  const { logout, state } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const user = state.status === "authenticated" ? state.user : null;

  return (
    <div className="app-layout">
      <SkipLink />
      <header className="app-header">
        <div className="app-header__container">
          <div className="app-header__brand-wrap">
            <Link to="/dashboard" className="brand">
              <span className="brand__logo">🥑</span>
              <span className="brand__text">Daily Plate</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav aria-label="Primary" className="desktop-nav">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `nav-link ${isActive ? "nav-link--active" : ""}`
                }
              >
                <span className="nav-link__icon">{link.icon}</span>
                <span className="nav-link__label">{link.label}</span>
              </NavLink>
            ))}
          </nav>

          {/* User Controls */}
          <div className="app-header__user-controls">
            {user && (
              <NavLink
                to="/profile"
                className={({ isActive }) =>
                  `user-profile-badge ${isActive ? "user-profile-badge--active" : ""}`
                }
                title="Profile settings"
              >
                <span className="user-profile-badge__avatar">👤</span>
                <span className="user-profile-badge__name">
                  {user.displayName || "My Account"}
                </span>
              </NavLink>
            )}

            <Button
              variant="outline"
              size="small"
              onClick={() => void logout()}
              className="logout-btn"
            >
              Log out
            </Button>

            {/* Mobile Hamburger Toggle */}
            <button
              type="button"
              className="mobile-menu-toggle"
              aria-label="Toggle navigation menu"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
            >
              {mobileMenuOpen ? "✕" : "☰"}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <nav aria-label="Mobile" className="mobile-nav">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `mobile-nav-link ${isActive ? "mobile-nav-link--active" : ""}`
                }
              >
                <span className="mobile-nav-link__icon">{link.icon}</span>
                <span>{link.label}</span>
              </NavLink>
            ))}
            <NavLink
              to="/profile"
              onClick={() => setMobileMenuOpen(false)}
              className="mobile-nav-link"
            >
              <span>⚙️</span>
              <span>Profile & Settings</span>
            </NavLink>
          </nav>
        )}
      </header>

      <main id="main-content" className="content">
        <Outlet />
      </main>
    </div>
  );
}
