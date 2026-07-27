"""Speech utilities.

Browser Web Speech API handles real-time STT on the client.
This endpoint accepts uploaded audio and returns a transcript via OpenAI Whisper
when an API key is configured; otherwise returns a helpful fallback message.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.auth import CurrentUser
from app.config import get_settings
from app.schemas import TranscribeResponse

router = APIRouter(prefix="/speech", tags=["speech"])
settings = get_settings()


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(_: CurrentUser, file: UploadFile = File(...)):
    if not settings.openai_api_key:
        # Client should prefer Web Speech API; this is a server-side fallback.
        raise HTTPException(
            status_code=503,
            detail=(
                "Server transcription requires OPENAI_API_KEY. "
                "Use browser voice mode (Web Speech API) which works without a key."
            ),
        )

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # OpenAI SDK expects a file-like tuple
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=(file.filename or "audio.webm", content, file.content_type or "audio/webm"),
    )
    return TranscribeResponse(text=transcript.text, language=getattr(transcript, "language", None))
