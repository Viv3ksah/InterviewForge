import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import AppShell from "../components/AppShell";

export default function History() {
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listInterviews()
      .then(setSessions)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <AppShell>
      <section className="page-head">
        <div>
          <p className="eyebrow">History</p>
          <h1>Interview sessions</h1>
          <p className="muted">Review past mocks and jump back into results.</p>
        </div>
        <Link to="/interview/new" className="btn primary">
          New interview
        </Link>
      </section>
      {error && <p className="form-error">{error}</p>}
      <div className="history-list">
        {sessions.length === 0 && <p className="muted">No sessions yet.</p>}
        {sessions.map((s) => (
          <Link
            key={s.id}
            className="history-item"
            to={s.status === "completed" ? `/results/${s.id}` : `/interview/${s.id}`}
          >
            <div>
              <strong>{s.role}</strong>
              <p className="muted">
                {s.domain} · {s.difficulty} · {s.mode} · {s.question_count} Qs
              </p>
            </div>
            <div className="history-meta">
              <span className={`status ${s.status}`}>{s.status.replace("_", " ")}</span>
              <strong>{s.overall_score != null ? `${s.overall_score}` : "—"}</strong>
              <span className="muted">{new Date(s.created_at).toLocaleString()}</span>
            </div>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}
