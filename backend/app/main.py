from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import auth, dashboard, interviews, speech

settings = get_settings()

app = FastAPI(
    title="InterviewForge API",
    description="AI-powered mock interview platform — DSA, System Design, HR, voice mode.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins + ["http://localhost:4173", "http://127.0.0.1:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(interviews.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(speech.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "InterviewForge",
        "llm_enabled": bool(settings.openai_api_key),
    }
