import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
export function ProtectedRoute(): React.JSX.Element { const { state } = useAuth(); const location = useLocation(); if (state.status === "initializing") return <main className="page-shell"><p>Preparing your tracker…</p></main>; return state.status === "authenticated" ? <Outlet /> : <Navigate to="/login" replace state={{ from: location.pathname }} />; }
