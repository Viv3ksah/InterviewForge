import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="landing">
      <div className="landing-atmosphere" aria-hidden />
      <header className="landing-nav">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden />
          <span className="brand-name">InterviewForge</span>
        </div>
        <div className="landing-nav-actions">
          <Link to="/login" className="btn ghost">
            Log in
          </Link>
          <Link to="/register" className="btn primary">
            Start practicing
          </Link>
        </div>
      </header>

      <section className="hero">
        <p className="brand-hero">InterviewForge</p>
        <h1>Practice like the real interview — with AI that coaches you back.</h1>
        <p className="hero-sub">
          Role-specific DSA, System Design, and HR rounds with live feedback, voice answers, and a
          dashboard that shows exactly where to improve next.
        </p>
        <div className="hero-cta">
          <Link to="/register" className="btn primary large">
            Create free account
          </Link>
          <Link to="/login" className="btn outline large">
            I already have an account
          </Link>
        </div>
      </section>

      <section className="feature-strip">
        <article>
          <h2>LLM-generated questions</h2>
          <p>Tailored to your role, difficulty, and company style across technical and behavioral domains.</p>
        </article>
        <article>
          <h2>Voice interview mode</h2>
          <p>Speak your answers with real-time speech-to-text for a more realistic pressure environment.</p>
        </article>
        <article>
          <h2>Performance dashboard</h2>
          <p>Track scores, trends, strengths, and personalized practice recommendations over time.</p>
        </article>
      </section>
    </div>
  );
}
