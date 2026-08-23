# JanSetu Backend — Layer 2 (ingestion pipeline) + Layer 3 (clustering/scoring)

## Setup

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in MONGODB_URI at minimum
```

Whisper needs `ffmpeg` on the system (not a pip package):
```bash
# macOS: brew install ffmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
```
If you don't have time to sort this out tonight, **you don't have to** — `pipeline/stt.py`
automatically falls back to a stub transcription if `whisper` fails to import, so the rest
of the pipeline (classify → geocode → score) still runs and is demoable. Swap it for real
Whisper output whenever it's working; nothing else needs to change.

Same deal with LangGraph (`pipeline/graph.py`) — if install is problematic, it silently
falls back to a plain sequential function chain with identical behavior.

ElevenLabs TTS confirmation is opt-in: leave `ELEVENLABS_API_KEY` blank in `.env` and
`confirmation_audio_url` will just be `null` in responses, which the API contract already
allows for.

## Run order

```bash
# 1. Start the API
uvicorn main:app --reload --port 8000

# 2. In a separate terminal, seed synthetic demo data (so clustering has something to work with)
python -m seed.seed_requests

# 3. Compute hotspots from the seeded data
python -m scoring.run_scoring

# 4. Confirm it worked
curl http://localhost:8000/api/hotspots
```

From here, `POST /api/requests` with real voice/text input will add more requests, and
`POST /api/hotspots/recompute` re-runs clustering/scoring on demand — useful for the demo:
submit a couple of live reports, hit recompute, show the ranked list change.

## What's real vs. what's scoped down for the hackathon

| Piece | Status |
|---|---|
| Whisper STT + translation | Real (local model), stub fallback if unavailable |
| Classification | Real, but keyword-based — not an ML model (see `pipeline/classify.py` for why, and how to swap in an LLM call) |
| Geocoding | Real (Nominatim/OpenStreetMap, free tier) |
| Clustering (DBSCAN) | Real |
| Deprivation index | Static seed table (`data/deprivation_index.json`) — illustrative values, not sourced from an official dataset. Say this openly in the pitch; swapping in real NITI Aayog/Census figures is a stated next step, not a hidden gap |
| Scheme alignment | Static lookup table, but maps to real, named government schemes |
| WhatsApp/IVR integration | Not built — architecturally, any channel just needs to call `POST /api/requests` with the same shape (see `API_CONTRACT.md`) |

## Deploying (Render)

- New Web Service → point at `backend/`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Set env vars from `.env.example` in Render's dashboard
- Whisper + torch make the image large and the first boot slow — if Render's free tier
  struggles, that's your cue to lean on the stub fallback for the live demo and mention
  local Whisper output in the video instead.
