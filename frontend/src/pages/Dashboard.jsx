import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";
import AppShell from "../components/AppShell";
import { useAuth } from "../AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .dashboard()
      .then(setStats)
      .catch((e) => setError(e.message));
  }, []);

  const chartData = [...(stats?.recent_scores || [])]
    .reverse()
    .map((s) => ({
      name: new Date(s.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      score: s.score,
      domain: s.domain,
    }));

  return (
    <AppShell>
      <section className="page-head">
        <div>
          <p className="eyebrow">Candidate dashboard</p>
          <h1>Welcome back, {user?.full_name?.split(" ")[0]}</h1>
          <p className="muted">
            {user?.target_role || "Software Engineer"} · {user?.experience_level || "Mid-level"}
          </p>
        </div>
        <Link to="/interview/new" className="btn primary">
          Start mock interview
        </Link>
      </section>

      {error && <p className="form-error">{error}</p>}

      <section className="stat-row">
        <div className="stat">
          <span>Sessions</span>
          <strong>{stats?.total_sessions ?? "—"}</strong>
        </div>
        <div className="stat">
          <span>Completed</span>
          <strong>{stats?.completed_sessions ?? "—"}</strong>
        </div>
        <div className="stat">
          <span>Average score</span>
          <strong>{stats?.average_score ?? "—"}</strong>
        </div>
        <div className="stat">
          <span>Best score</span>
          <strong>{stats?.best_score ?? "—"}</strong>
        </div>
      </section>

      <section className="dash-grid">
        <div className="panel">
          <h2>Performance trend</h2>
          {chartData.length ? (
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={chartData}>
                  <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                  <XAxis dataKey="name" stroke="#8b9bb4" fontSize={12} />
                  <YAxis domain={[0, 100]} stroke="#8b9bb4" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      background: "#121a2b",
                      border: "1px solid rgba(61,214,198,0.25)",
                      borderRadius: 8,
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#3dd6c6"
                    strokeWidth={3}
                    dot={{ r: 4, fill: "#3dd6c6" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="muted">Complete an interview to see your score trend.</p>
          )}
        </div>

        <div className="panel">
          <h2>Domain averages</h2>
          {stats?.domain_averages && Object.keys(stats.domain_averages).length ? (
            <ul className="domain-list">
              {Object.entries(stats.domain_averages).map(([domain, score]) => (
                <li key={domain}>
                  <span>{domain}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${score}%` }} />
                  </div>
                  <strong>{score}</strong>
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">Domain breakdown appears after scored sessions.</p>
          )}
        </div>

        <div className="panel">
          <h2>Strengths</h2>
          <ul className="bullet-list">
            {(stats?.strengths || []).map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </div>

        <div className="panel">
          <h2>Focus areas</h2>
          <ul className="bullet-list warn">
            {(stats?.focus_areas || []).map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </div>

        <div className="panel span-2">
          <h2>Personalized practice recommendations</h2>
          <ul className="rec-list">
            {(stats?.recommendations || []).map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </div>
      </section>
    </AppShell>
  );
}
