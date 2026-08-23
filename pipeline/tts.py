"""
Generates a spoken confirmation via ElevenLabs, saved to /static and served
by FastAPI's StaticFiles mount (see main.py). Fully optional — if
ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID aren't set, this is skipped and
confirmation_audio_url stays null (the API contract already allows for that).
"""
import os
import uuid

from config import USE_ELEVENLABS, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


def generate_confirmation(text: str, request_id: str) -> str | None:
    if not USE_ELEVENLABS:
        return None

    try:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE_ID,
            text=f"Thank you. We recorded your report: {text}",
            model_id="eleven_multilingual_v2",
        )
        os.makedirs(STATIC_DIR, exist_ok=True)
        filename = f"confirm_{request_id}_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(STATIC_DIR, filename)
        with open(filepath, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        return f"/static/{filename}"
    except Exception:
        # TTS is a nice-to-have, not a critical-path failure — never let it break the pipeline.
        return None
