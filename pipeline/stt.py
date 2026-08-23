"""
Speech-to-text using OpenAI's local Whisper model.

We use task="translate" (not "transcribe") — Whisper does language detection
AND translation-to-English in a single call, which removes the need for a
separate translation step in the pipeline.

If whisper isn't installed / ffmpeg is missing / anything goes wrong, this
falls back to a stub so the rest of the pipeline (classify -> geocode ->
persist) still runs end-to-end during development. Swap USE_STUB off once
whisper is confirmed working in your environment.
"""
import base64
import os
import tempfile

_model = None
_STUB_MODE = False

try:
    import whisper  # openai-whisper
except ImportError:
    whisper = None
    _STUB_MODE = True


def _get_model():
    global _model
    if _model is None and whisper is not None:
        from config import WHISPER_MODEL_SIZE
        _model = whisper.load_model(WHISPER_MODEL_SIZE)
    return _model


def transcribe_and_translate(audio_base64: str) -> dict:
    """
    Returns: {"english_text": str, "language_detected": str}
    """
    if _STUB_MODE or whisper is None:
        return {
            "english_text": "[stt stub — whisper not installed] There is a problem in my area that needs attention.",
            "language_detected": "unknown",
        }

    audio_bytes = base64.b64decode(audio_base64)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        model = _get_model()
        result = model.transcribe(tmp_path, task="translate")
        return {
            "english_text": result.get("text", "").strip(),
            "language_detected": result.get("language", "unknown"),
        }
    finally:
        os.unlink(tmp_path)


def passthrough_text(text: str, language_hint: str | None) -> dict:
    """For input_type == 'text' — no STT needed, just normalize the shape."""
    return {
        "english_text": text.strip(),
        "language_detected": language_hint or "en",
    }
