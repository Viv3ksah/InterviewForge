from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field

Domain = Literal["DSA", "System Design", "HR", "Mixed"]
Difficulty = Literal["Easy", "Medium", "Hard"]
Mode = Literal["text", "voice"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    target_role: str | None = None
    experience_level: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    target_role: str | None = None
    experience_level: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    target_role: str | None = None
    experience_level: str | None = None


class SessionCreate(BaseModel):
    role: str = Field(default="Software Engineer", max_length=120)
    domain: Domain = "Mixed"
    difficulty: Difficulty = "Medium"
    mode: Mode = "text"
    company_style: str | None = Field(default=None, max_length=80)
    question_count: int = Field(default=5, ge=3, le=10)
    duration_minutes: int = Field(default=30, ge=10, le=90)


class QuestionOut(BaseModel):
    id: int
    order_index: int
    domain: str
    prompt: str
    hints: list[str] | None = None
    expected_topics: list[str] | None = None
    answer_text: str | None = None
    transcribed: bool = False
    score: float | None = None
    feedback: str | None = None
    strengths: list[str] | None = None
    improvements: list[str] | None = None
    follow_up: str | None = None
    answered_at: datetime | None = None

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: int
    role: str
    domain: str
    difficulty: str
    mode: str
    company_style: str | None = None
    status: str
    duration_minutes: int
    overall_score: float | None = None
    summary: str | None = None
    strengths: list[str] | None = None
    improvements: list[str] | None = None
    recommendations: list[str] | None = None
    score_breakdown: dict[str, Any] | None = None
    created_at: datetime
    completed_at: datetime | None = None
    questions: list[QuestionOut] = []

    model_config = {"from_attributes": True}


class SessionSummary(BaseModel):
    id: int
    role: str
    domain: str
    difficulty: str
    mode: str
    status: str
    overall_score: float | None = None
    created_at: datetime
    completed_at: datetime | None = None
    question_count: int = 0

    model_config = {"from_attributes": True}


class AnswerSubmit(BaseModel):
    answer_text: str = Field(min_length=1, max_length=12000)
    transcribed: bool = False


class TranscribeResponse(BaseModel):
    text: str
    language: str | None = None


class DashboardStats(BaseModel):
    total_sessions: int
    completed_sessions: int
    average_score: float | None
    best_score: float | None
    domain_averages: dict[str, float]
    recent_scores: list[dict[str, Any]]
    recommendations: list[str]
    strengths: list[str]
    focus_areas: list[str]
