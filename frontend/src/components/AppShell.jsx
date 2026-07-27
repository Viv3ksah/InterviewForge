import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function AppShell({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="shell">
      <header className="topbar">
        <button className="brand-lockup" type="button" onClick={() => navigate("/dashboard")}>
          <span className="brand-mark" aria-hidden />
          <span className="brand-name">InterviewForge</span>
        </button>
        <nav className="topnav">
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/interview/new">New Interview</NavLink>
          <NavLink to="/history">History</NavLink>
        </nav>
        <div className="topbar-user">
          <span className="user-chip">{user?.full_name?.split(" ")[0]}</span>
          <button
            type="button"
            className="btn ghost"
            onClick={() => {
              logout();
              navigate("/");
            }}
          >
            Log out
          </button>
        </div>
      </header>
      <main className="shell-main">{children}</main>
    </div>
  );
}
