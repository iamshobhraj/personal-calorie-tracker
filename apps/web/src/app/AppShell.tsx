import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../state/auth/AuthContext";
import { Button } from "../components/Button";
import { SkipLink } from "../components/SkipLink";
const links = [["/dashboard", "Dashboard"], ["/meals", "Meals"], ["/goals", "Goals"], ["/analyze", "Analyze"], ["/reports", "Reports"], ["/profile", "Profile"]] as const;
export function AppShell(): React.JSX.Element { const { logout, state } = useAuth(); return <><SkipLink /><header className="app-header"><NavLink to="/dashboard" className="brand">Daily Plate</NavLink><nav aria-label="Primary">{links.map(([to, label]) => <NavLink key={to} to={to}>{label}</NavLink>)}</nav><Button onClick={() => void logout()}>{state.status === "authenticated" ? "Log out" : ""}</Button></header><main id="main-content" className="content"><Outlet /></main></>; }
