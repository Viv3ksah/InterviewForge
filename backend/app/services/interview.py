from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models import InterviewSession, Question, User
from app.services import llm as llm_service


def create_session(
    db: Session,
    user: User,
    *,
    role: str,
    domain: str,
    difficulty: str,
    mode: str,
    company_style: str | None,
    question_count: int,
    duration_minutes: int,
) -> InterviewSession:
    questions_data = llm_service.generate_questions(
        role=role,
        domain=domain,
        difficulty=difficulty,
        count=question_count,
        company_style=company_style,
        experience_level=user.experience_level,
    )
    session = InterviewSession(
        user_id=user.id,
        role=role,
        domain=domain,
        difficulty=difficulty,
        mode=mode,
        company_style=company_style,
        duration_minutes=duration_minutes,
        status="in_progress",
    )
    db.add(session)
    db.flush()

    for idx, q in enumerate(questions_data):
        db.add(
            Question(
                session_id=session.id,
                order_index=idx,
                domain=q["domain"],
                prompt=q["prompt"],
                hints=q.get("hints") or [],
                expected_topics=q.get("expected_topics") or [],
            )
        )
    db.commit()
    return (
        db.query(InterviewSession)
        .options(joinedload(InterviewSession.questions))
        .filter(InterviewSession.id == session.id)
        .one()
    )


def submit_answer(db: Session, user: User, session_id: int, question_id: int, answer_text: str, transcribed: bool) -> Question:
    session = (
        db.query(InterviewSession)
        .options(joinedload(InterviewSession.questions))
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == user.id)
        .one_or_none()
    )
    if not session:
        raise ValueError("Session not found")
    if session.status == "completed":
        raise ValueError("Session already completed")

    question = next((q for q in session.questions if q.id == question_id), None)
    if not question:
        raise ValueError("Question not found")

    evaluation = llm_service.evaluate_answer(
        question=question.prompt,
        answer=answer_text,
        domain=question.domain,
        role=session.role,
        expected_topics=question.expected_topics or [],
    )
    question.answer_text = answer_text
    question.transcribed = transcribed
    question.score = evaluation["score"]
    question.feedback = evaluation["feedback"]
    question.strengths = evaluation["strengths"]
    question.improvements = evaluation["improvements"]
    question.follow_up = evaluation.get("follow_up")
    question.answered_at = datetime.utcnow()
    db.commit()
    db.refresh(question)
    return question


def complete_session(db: Session, user: User, session_id: int) -> InterviewSession:
    session = (
        db.query(InterviewSession)
        .options(joinedload(InterviewSession.questions))
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == user.id)
        .one_or_none()
    )
    if not session:
        raise ValueError("Session not found")

    answered = [q for q in session.questions if q.answer_text]
    if not answered:
        raise ValueError("Answer at least one question before completing")

    payload = [
        {
            "domain": q.domain,
            "prompt": q.prompt,
            "score": q.score,
            "strengths": q.strengths,
            "improvements": q.improvements,
            "feedback": q.feedback,
        }
        for q in answered
    ]
    summary = llm_service.summarize_session(session.role, session.domain, payload)
    scores = [q.score or 0 for q in answered]
    session.overall_score = round(sum(scores) / len(scores), 1)
    session.summary = summary["summary"]
    session.strengths = summary["strengths"]
    session.improvements = summary["improvements"]
    session.recommendations = summary["recommendations"]
    session.score_breakdown = summary["score_breakdown"]
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def build_dashboard(db: Session, user: User) -> dict:
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user.id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )
    completed = [s for s in sessions if s.status == "completed" and s.overall_score is not None]
    scores = [s.overall_score for s in completed if s.overall_score is not None]

    domain_buckets: dict[str, list[float]] = defaultdict(list)
    for s in completed:
        if s.score_breakdown:
            for domain, value in s.score_breakdown.items():
                domain_buckets[domain].append(float(value))
        elif s.overall_score is not None:
            domain_buckets[s.domain].append(s.overall_score)

    domain_averages = {k: round(sum(v) / len(v), 1) for k, v in domain_buckets.items()}
    recent_scores = [
        {
            "id": s.id,
            "role": s.role,
            "domain": s.domain,
            "score": s.overall_score,
            "created_at": s.created_at.isoformat(),
            "mode": s.mode,
        }
        for s in completed[:8]
    ]

    # Aggregate recommendations / strengths / focus areas
    recs: list[str] = []
    strengths: list[str] = []
    focus: list[str] = []
    for s in completed[:5]:
        recs.extend(s.recommendations or [])
        strengths.extend(s.strengths or [])
        focus.extend(s.improvements or [])

    if not completed:
        recs = [
            "Start with a Mixed Medium interview to baseline your skills",
            "Try voice mode once to practice spoken clarity",
            "Focus DSA patterns: arrays, trees, and sliding windows",
        ]
        strengths = ["Ready to begin your practice journey"]
        focus = ["Complete your first mock interview"]

    # Deduplicate preserving order
    def uniq(items: list[str], limit: int = 5) -> list[str]:
        seen = set()
        out = []
        for i in items:
            key = i.strip().lower()
            if key and key not in seen:
                seen.add(key)
                out.append(i)
            if len(out) >= limit:
                break
        return out

    return {
        "total_sessions": len(sessions),
        "completed_sessions": len(completed),
        "average_score": round(sum(scores) / len(scores), 1) if scores else None,
        "best_score": max(scores) if scores else None,
        "domain_averages": domain_averages,
        "recent_scores": recent_scores,
        "recommendations": uniq(recs),
        "strengths": uniq(strengths),
        "focus_areas": uniq(focus),
    }
