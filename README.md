# InterviewForge

AI-powered mock interview platform for DSA, System Design, and HR practice.

**Stack:** Python (FastAPI) · OpenAI LLM APIs · React (Vite) · SQLAlchemy/SQLite · Web Speech API + Whisper

## Features

- Role-specific interview question generation (DSA / System Design / HR / Mixed)
- AI answer evaluation with strengths, improvements, and follow-ups
- Voice interview mode with real-time speech-to-text (browser Web Speech API)
- Candidate dashboard with score trends, domain averages, and practice recommendations
- Secure JWT authentication and REST APIs
- Timed sessions, difficulty levels, and company-style customization
- Works offline from LLM keys using built-in heuristic fallbacks (add `OPENAI_API_KEY` for full AI)

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # or: cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Optional in `.env`:

```
OPENAI_API_KEY=sk-...
```

API docs: http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173

The Vite dev server proxies `/api` to the FastAPI backend.

## Project structure

```
backend/app/          FastAPI app, auth, models, LLM services, routers
frontend/src/         React UI — landing, auth, dashboard, interview room, results
```

## API overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/dashboard/stats` | Performance dashboard |
| POST | `/api/interviews` | Start session + generate questions |
| POST | `/api/interviews/{id}/questions/{qid}/answer` | Submit + evaluate answer |
| POST | `/api/interviews/{id}/complete` | Finalize session report |
| POST | `/api/speech/transcribe` | Whisper transcription (requires API key) |

## License

MIT
