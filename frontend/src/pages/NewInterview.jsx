import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import AppShell from "../components/AppShell";
import { useAuth } from "../AuthContext";

export default function NewInterview() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    role: user?.target_role || "Software Engineer",
    domain: "Mixed",
    difficulty: "Medium",
    mode: "text",
    company_style: "General tech",
    question_count: 5,
    duration_minutes: 30,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function update(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const session = await api.startInterview({
        ...form,
        question_count: Number(form.question_count),
        duration_minutes: Number(form.duration_minutes),
      });
      navigate(`/interview/${session.id}`);
    } catch (err) {
      setError(err.message || "Could not start interview");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <section className="page-head">
        <div>
          <p className="eyebrow">New session</p>
          <h1>Configure your mock interview</h1>
          <p className="muted">Choose domain, difficulty, and text or voice mode.</p>
        </div>
      </section>

      <form className="setup-form panel" onSubmit={onSubmit}>
        <label>
          Target role
          <input value={form.role} onChange={(e) => update("role", e.target.value)} required />
        </label>
        <label>
          Domain
          <select value={form.domain} onChange={(e) => update("domain", e.target.value)}>
            <option>Mixed</option>
            <option>DSA</option>
            <option>System Design</option>
            <option>HR</option>
          </select>
        </label>
        <label>
          Difficulty
          <select value={form.difficulty} onChange={(e) => update("difficulty", e.target.value)}>
            <option>Easy</option>
            <option>Medium</option>
            <option>Hard</option>
          </select>
        </label>
        <label>
          Mode
          <select value={form.mode} onChange={(e) => update("mode", e.target.value)}>
            <option value="text">Text</option>
            <option value="voice">Voice (speech-to-text)</option>
          </select>
        </label>
        <label>
          Company style
          <input
            value={form.company_style}
            onChange={(e) => update("company_style", e.target.value)}
            placeholder="e.g. FAANG, Startup, FinTech"
          />
        </label>
        <label>
          Questions
          <input
            type="number"
            min={3}
            max={10}
            value={form.question_count}
            onChange={(e) => update("question_count", e.target.value)}
          />
        </label>
        <label>
          Duration (minutes)
          <input
            type="number"
            min={10}
            max={90}
            value={form.duration_minutes}
            onChange={(e) => update("duration_minutes", e.target.value)}
          />
        </label>
        {error && <p className="form-error span-all">{error}</p>}
        <button className="btn primary large span-all" disabled={busy} type="submit">
          {busy ? "Generating questions…" : "Begin interview"}
        </button>
      </form>
    </AppShell>
  );
}
