import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import AppShell from "../components/AppShell";

function getSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  return SpeechRecognition ? new SpeechRecognition() : null;
}

export default function InterviewRoom() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [listening, setListening] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [secondsLeft, setSecondsLeft] = useState(null);
  const recognitionRef = useRef(null);
  const baseAnswerRef = useRef("");

  const load = useCallback(() => {
    api
      .getInterview(id)
      .then((s) => {
        setSession(s);
        setSecondsLeft((s.duration_minutes || 30) * 60);
        const firstUnanswered = s.questions.findIndex((q) => !q.answer_text);
        setIndex(firstUnanswered >= 0 ? firstUnanswered : 0);
        if (s.status === "completed") navigate(`/results/${s.id}`, { replace: true });
      })
      .catch((e) => setError(e.message));
  }, [id, navigate]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (secondsLeft == null || !session || session.status === "completed") return undefined;
    if (secondsLeft <= 0) return undefined;
    const t = setInterval(() => setSecondsLeft((s) => (s > 0 ? s - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, [secondsLeft, session]);

  const question = session?.questions?.[index];
  const answeredCount = useMemo(
    () => session?.questions?.filter((q) => q.answer_text)?.length || 0,
    [session]
  );

  function stopListening() {
    recognitionRef.current?.stop();
    setListening(false);
  }

  function startListening() {
    const recognition = getSpeechRecognition();
    if (!recognition) {
      setError("Speech recognition is not supported in this browser. Try Chrome, or type your answer.");
      return;
    }
    baseAnswerRef.current = answer;
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    recognition.onresult = (event) => {
      let interim = "";
      let finalChunk = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalChunk += `${transcript} `;
        else interim += transcript;
      }
      if (finalChunk) {
        baseAnswerRef.current = `${baseAnswerRef.current} ${finalChunk}`.replace(/\s+/g, " ").trim();
      }
      setAnswer(`${baseAnswerRef.current}${interim ? ` ${interim}` : ""}`.trim());
    };
    recognition.onerror = () => setListening(false);
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
    setError("");
  }

  async function submitAnswer() {
    if (!question || !answer.trim()) return;
    stopListening();
    setBusy(true);
    setError("");
    try {
      const updated = await api.answerQuestion(session.id, question.id, {
        answer_text: answer.trim(),
        transcribed: session.mode === "voice" || listening,
      });
      setFeedback(updated);
      setSession((prev) => ({
        ...prev,
        questions: prev.questions.map((q) => (q.id === updated.id ? updated : q)),
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function nextQuestion() {
    setFeedback(null);
    setAnswer("");
    if (index < session.questions.length - 1) setIndex((i) => i + 1);
  }

  async function finish() {
    setBusy(true);
    try {
      const completed = await api.completeInterview(session.id);
      navigate(`/results/${completed.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (!session || !question) {
    return (
      <AppShell>
        <div className="loading-screen compact">
          <div className="pulse-orb" />
          <p>{error || "Preparing your interview…"}</p>
        </div>
      </AppShell>
    );
  }

  const mm = String(Math.floor((secondsLeft || 0) / 60)).padStart(2, "0");
  const ss = String((secondsLeft || 0) % 60).padStart(2, "0");

  return (
    <AppShell>
      <section className="interview-meta">
        <div>
          <p className="eyebrow">
            {session.domain} · {session.difficulty} · {session.mode}
          </p>
          <h1>{session.role}</h1>
        </div>
        <div className="timer" data-urgent={secondsLeft < 60}>
          {mm}:{ss}
        </div>
      </section>

      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${((index + 1) / session.questions.length) * 100}%` }}
        />
      </div>
      <p className="muted">
        Question {index + 1} of {session.questions.length} · {answeredCount} answered
      </p>

      <article className="question-panel">
        <span className="domain-tag">{question.domain}</span>
        <h2>{question.prompt}</h2>
        {question.hints?.length > 0 && (
          <details className="hints">
            <summary>Hints</summary>
            <ul>
              {question.hints.map((h) => (
                <li key={h}>{h}</li>
              ))}
            </ul>
          </details>
        )}
      </article>

      {!feedback ? (
        <section className="answer-panel">
          <div className="answer-toolbar">
            <label htmlFor="answer">Your answer</label>
            {(session.mode === "voice" || true) && (
              <button
                type="button"
                className={`btn mic ${listening ? "listening" : ""}`}
                onClick={() => (listening ? stopListening() : startListening())}
              >
                {listening ? "Stop listening" : "Speak answer"}
              </button>
            )}
          </div>
          <textarea
            id="answer"
            rows={10}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder={
              session.mode === "voice"
                ? "Click Speak answer and talk — your words appear here in real time."
                : "Type your answer with structure, trade-offs, and examples…"
            }
          />
          {error && <p className="form-error">{error}</p>}
          <button className="btn primary" disabled={busy || !answer.trim()} onClick={submitAnswer}>
            {busy ? "Evaluating…" : "Submit for AI feedback"}
          </button>
        </section>
      ) : (
        <section className="feedback-panel">
          <div className="score-pill">{Math.round(feedback.score)} / 100</div>
          <h3>Feedback</h3>
          <p>{feedback.feedback}</p>
          <div className="two-col">
            <div>
              <h4>Strengths</h4>
              <ul>
                {(feedback.strengths || []).map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4>Improve</h4>
              <ul>
                {(feedback.improvements || []).map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          </div>
          {feedback.follow_up && (
            <p className="follow-up">
              <strong>Follow-up:</strong> {feedback.follow_up}
            </p>
          )}
          <div className="action-row">
            {index < session.questions.length - 1 ? (
              <button className="btn primary" onClick={nextQuestion}>
                Next question
              </button>
            ) : (
              <button className="btn primary" disabled={busy} onClick={finish}>
                {busy ? "Wrapping up…" : "Complete interview"}
              </button>
            )}
            {answeredCount > 0 && index < session.questions.length - 1 && (
              <button className="btn outline" disabled={busy} onClick={finish}>
                Finish early
              </button>
            )}
          </div>
        </section>
      )}
    </AppShell>
  );
}
