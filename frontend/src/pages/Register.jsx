import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    target_role: "Software Engineer",
    experience_level: "Mid-level",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function update(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register(form);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || "Registration failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-panel wide">
        <Link to="/" className="brand-lockup compact">
          <span className="brand-mark" aria-hidden />
          <span className="brand-name">InterviewForge</span>
        </Link>
        <h1>Build your interview edge</h1>
        <p className="muted">Create an account to track progress and unlock voice practice.</p>
        <form onSubmit={onSubmit} className="auth-form grid-2">
          <label>
            Full name
            <input value={form.full_name} onChange={(e) => update("full_name", e.target.value)} required />
          </label>
          <label>
            Target role
            <input value={form.target_role} onChange={(e) => update("target_role", e.target.value)} />
          </label>
          <label>
            Email
            <input
              type="email"
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              required
            />
          </label>
          <label>
            Experience
            <select value={form.experience_level} onChange={(e) => update("experience_level", e.target.value)}>
              <option>Intern</option>
              <option>Junior</option>
              <option>Mid-level</option>
              <option>Senior</option>
              <option>Staff+</option>
            </select>
          </label>
          <label className="span-2">
            Password
            <input
              type="password"
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              required
              minLength={6}
            />
          </label>
          {error && <p className="form-error span-2">{error}</p>}
          <button className="btn primary full span-2" disabled={busy} type="submit">
            {busy ? "Creating…" : "Create account"}
          </button>
        </form>
        <p className="muted center">
          Already practicing? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
}
