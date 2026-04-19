"""OpenAI Whisper STT wrapper — stub.

Owner: Track-5. Called by the /battles/{id}/answer endpoint when
audio_blob_b64 is present. Decode base64 -> temp file -> whisper API.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from openai import OpenAI

from ..config import settings


def get_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


async def transcribe(audio_bytes: bytes) -> str:
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError(
            "Local Whisper not installed. Install `openai-whisper` for voice transcription."
        ) from exc

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = Path(tmp.name)

    try:
        model = whisper.load_model("base")
        result = model.transcribe(str(tmp_path))
        text = result.get("text", "") if isinstance(result, dict) else ""
        return text.strip()
    finally:
        tmp_path.unlink(missing_ok=True)
