from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import joinedload

from app.auth import CurrentUser, DbSession
from app.models import InterviewSession
from app.schemas import AnswerSubmit, QuestionOut, SessionCreate, SessionOut, SessionSummary
from app.services import interview as interview_service

router = APIRouter(prefix="/interviews", tags=["interviews"])


def _session_out(session: InterviewSession) -> SessionOut:
    questions = sorted(session.questions, key=lambda q: q.order_index)
    return SessionOut(
        id=session.id,
        role=session.role,
        domain=session.domain,
        difficulty=session.difficulty,
        mode=session.mode,
        company_style=session.company_style,
        status=session.status,
        duration_minutes=session.duration_minutes,
        overall_score=session.overall_score,
        summary=session.summary,
        strengths=session.strengths,
        improvements=session.improvements,
        recommendations=session.recommendations,
        score_breakdown=session.score_breakdown,
        created_at=session.created_at,
        completed_at=session.completed_at,
        questions=[QuestionOut.model_validate(q) for q in questions],
    )


@router.post("", response_model=SessionOut, status_code=201)
def start_interview(payload: SessionCreate, user: CurrentUser, db: DbSession):
    session = interview_service.create_session(
        db,
        user,
        role=payload.role,
        domain=payload.domain,
        difficulty=payload.difficulty,
        mode=payload.mode,
        company_style=payload.company_style,
        question_count=payload.question_count,
        duration_minutes=payload.duration_minutes,
    )
    return _session_out(session)


@router.get("", response_model=list[SessionSummary])
def list_interviews(user: CurrentUser, db: DbSession):
    sessions = (
        db.query(InterviewSession)
        .options(joinedload(InterviewSession.questions))
        .filter(InterviewSession.user_id == user.id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )
    return [
        SessionSummary(
            id=s.id,
            role=s.role,
            domain=s.domain,
            difficulty=s.difficulty,
            mode=s.mode,
            status=s.status,
            overall_score=s.overall_score,
            created_at=s.created_at,
            completed_at=s.completed_at,
            question_count=len(s.questions),
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionOut)
def get_interview(session_id: int, user: CurrentUser, db: DbSession):
    session = (
        db.query(InterviewSession)
        .options(joinedload(InterviewSession.questions))
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == user.id)
        .one_or_none()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_out(session)


@router.post("/{session_id}/questions/{question_id}/answer", response_model=QuestionOut)
def answer_question(
    session_id: int,
    question_id: int,
    payload: AnswerSubmit,
    user: CurrentUser,
    db: DbSession,
):
    try:
        question = interview_service.submit_answer(
            db,
            user,
            session_id,
            question_id,
            payload.answer_text.strip(),
            payload.transcribed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return QuestionOut.model_validate(question)


@router.post("/{session_id}/complete", response_model=SessionOut)
def complete_interview(session_id: int, user: CurrentUser, db: DbSession):
    try:
        session = interview_service.complete_session(db, user, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # reload with questions
    session = (
        db.query(InterviewSession)
        .options(joinedload(InterviewSession.questions))
        .filter(InterviewSession.id == session.id)
        .one()
    )
    return _session_out(session)
