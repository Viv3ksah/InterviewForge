import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import AppShell from "../components/AppShell";

export default function Results() {
  const { id } = useParams();
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getInterview(id)
      .then(setSession)
      .catch((e) => setError(e.message));
  }, [id]);

  if (!session) {
    return (
      <AppShell>
        <div className="loading-screen compact">
          <div className="pulse-orb" />
          <p>{error || "Loading results…"}</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <section className="page-head">
        <div>
          <p className="eyebrow">Session report</p>
          <h1>{session.role}</h1>
          <p className="muted">
            {session.domain} · {session.difficulty} · {session.mode}
          </p>
        </div>
        <div className="action-row">
          <Link to="/dashboard" className="btn outline">
            Dashboard
          </Link>
          <Link to="/interview/new" className="btn primary">
            Practice again
          </Link>
        </div>
      </section>

      <section className="results-hero panel">
        <div className="big-score">
          <span>Overall</span>
          <strong>{session.overall_score ?? "—"}</strong>
        </div>
        <p>{session.summary}</p>
      </section>

      <section className="dash-grid">
        <div className="panel">
          <h2>Strengths</h2>
          <ul className="bullet-list">
            {(session.strengths || []).map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </div>
        <div className="panel">
          <h2>Areas to improve</h2>
          <ul className="bullet-list warn">
            {(session.improvements || []).map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </div>
        <div className="panel span-2">
          <h2>Recommendations</h2>
          <ul className="rec-list">
            {(session.recommendations || []).map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="panel" style={{ marginTop: "1.5rem" }}>
        <h2>Per-question breakdown</h2>
        <div className="qa-list">
          {session.questions.map((q, i) => (
            <details key={q.id} className="qa-item" open={i === 0}>
              <summary>
                <span>
                  Q{i + 1} · {q.domain}
                </span>
                <strong>{q.score != null ? q.score : "—"}</strong>
              </summary>
              <p className="q-prompt">{q.prompt}</p>
              {q.answer_text && (
                <p className="answer-preview">
                  <strong>Your answer:</strong> {q.answer_text}
                </p>
              )}
              {q.feedback && <p>{q.feedback}</p>}
            </details>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
