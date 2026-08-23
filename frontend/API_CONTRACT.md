# JanSetu — API Contract

Backend owner: you (Layers 2 & 3 — ingestion pipeline + clustering/scoring)
Frontend owner: teammate (Layers 1 & 4 — citizen intake + dashboard)

Base URL (once deployed): `https://<your-render-app>.onrender.com`
Local dev: `http://localhost:8000`

All requests/responses are JSON. All timestamps are ISO 8601 strings (UTC).

---

## 1. POST /api/requests

Used by: voice recorder, text form, and mock chat widget (all three call this same endpoint — that's the interoperability point of the whole architecture).

### Request body

```json
{
  "source": "voice",
  "input_type": "audio",
  "audio_base64": "<base64 string, only if input_type is audio>",
  "text": "<string, only if input_type is text>",
  "language_hint": "hi",
  "reported_location": {
    "lat": 28.6139,
    "lng": 77.2090,
    "place_name": "Sector 15, Rohini"
  }
}
```

Field notes:
- `source`: one of `"voice"`, `"text"`, `"chat"`
- `input_type`: one of `"audio"`, `"text"` — tells backend which of `audio_base64` / `text` to expect
- `language_hint`: optional, ISO 639-1 code (e.g. `"hi"`, `"en"`, `"ta"`) if the frontend knows it; backend will still auto-detect if omitted
- `reported_location`: optional. If the frontend has a location picker/GPS, send it. If omitted, backend will attempt to geocode from mentioned place names in the transcript — **frontend should not block submission on this being present**

### Success response — `202 Accepted`

```json
{
  "request_id": "665f1a2b3c4d5e6f7a8b9c0d",
  "status": "processing"
}
```

The pipeline (STT → classify → geocode) runs async. Frontend gets an ID back immediately for a "your report is being processed" state — **do not make the citizen wait on this call for the full pipeline to finish.**

### Poll for result — GET /api/requests/{request_id}

```json
{
  "request_id": "665f1a2b3c4d5e6f7a8b9c0d",
  "status": "done",
  "category": "water",
  "translated_text": "There has been no water supply in our area for five days",
  "language_detected": "hi",
  "district": "North West Delhi",
  "confirmation_audio_url": "https://.../confirm_665f1a2b.mp3"
}
```

`status` is one of `"processing"`, `"done"`, `"failed"`. Frontend should poll every ~2s, timeout/show error after ~20s.

`confirmation_audio_url` — the ElevenLabs read-back. Optional; may be `null` if TTS step is skipped for time.

### Error response — `400` / `500`

```json
{ "error": "missing_required_field", "message": "text is required when input_type is text" }
```

---

## 2. GET /api/hotspots

Used by: dashboard heatmap + ranked list.

### Query params (all optional)
- `category` — filter, e.g. `?category=water`
- `district` — filter, e.g. `?district=North West Delhi`

### Response — `200 OK`

```json
{
  "hotspots": [
    {
      "cluster_id": "cluster_04",
      "category": "water",
      "district": "North West Delhi",
      "center_lat": 28.6139,
      "center_lng": 77.2090,
      "request_count": 38,
      "priority_score": 87.4,
      "explainability_text": "38 requests clustered in this area, water infrastructure index in bottom quartile, aligns with Jal Jeevan Mission gap.",
      "rank": 1
    }
  ],
  "generated_at": "2026-08-24T02:15:00Z"
}
```

`priority_score` is 0–100. `rank` is precomputed by the backend — **frontend should not re-sort or re-rank, just display in the order given** (keeps scoring logic single-sourced).

### If hotspots haven't been computed yet — `200 OK`, empty array

```json
{ "hotspots": [], "generated_at": null }
```

Frontend should render an empty/loading state for this, not an error.

---

## 3. GET /api/requests (optional, for a raw feed view if you want one)

```json
{
  "requests": [
    {
      "request_id": "665f1a2b3c4d5e6f7a8b9c0d",
      "category": "water",
      "district": "North West Delhi",
      "source": "voice",
      "created_at": "2026-08-24T01:50:00Z"
    }
  ]
}
```

---

## Mock data for frontend to build against NOW

Don't wait on the real backend. Use this static JSON as a stand-in for `GET /api/hotspots` and build the dashboard against it — swap the fetch URL once the real endpoint is live. Drop this in `frontend/src/mock/hotspots.mock.json`:

```json
{
  "hotspots": [
    {
      "cluster_id": "cluster_01",
      "category": "water",
      "district": "North West Delhi",
      "center_lat": 28.7041,
      "center_lng": 77.1025,
      "request_count": 42,
      "priority_score": 91.2,
      "explainability_text": "42 requests clustered here, water infra index in bottom quartile, aligns with Jal Jeevan Mission gap.",
      "rank": 1
    },
    {
      "cluster_id": "cluster_02",
      "category": "road",
      "district": "South Delhi",
      "center_lat": 28.5245,
      "center_lng": 77.1855,
      "request_count": 27,
      "priority_score": 74.5,
      "explainability_text": "27 requests clustered here, road quality index below median, aligns with PMGSY connectivity gap.",
      "rank": 2
    },
    {
      "cluster_id": "cluster_03",
      "category": "electricity",
      "district": "East Delhi",
      "center_lat": 28.6280,
      "center_lng": 77.2900,
      "request_count": 15,
      "priority_score": 58.0,
      "explainability_text": "15 requests clustered here, frequent outages reported, moderate priority.",
      "rank": 3
    }
  ],
  "generated_at": "2026-08-24T02:15:00Z"
}
```

Same pattern for `POST /api/requests` — mock a `202` response with a fake `request_id`, and a mock `done` status after a couple seconds, so the intake flow's polling UI can be built and tested without hitting a real Whisper pipeline.

---

## Ground rules to avoid breakage at merge time

1. **Field names are frozen as written above.** If you need to change one, message first — don't silently rename on either side.
2. **Backend never removes a field**, only adds. Frontend should ignore fields it doesn't recognize (forward-compatible).
3. **CORS**: backend will allow the Vercel deployment origin + `localhost:5173` (or whatever Vite's dev port is) — tell her to confirm her local dev port.
4. **Env var for API base URL** on the frontend side (`VITE_API_BASE_URL`), not hardcoded — so switching from mock → local → deployed backend is a one-line change.
5. Merge/integration checkpoint: **agree on a specific time tonight** to swap mocks for the real endpoint and test the full loop together before recording the demo. Don't leave that for the final hour.
