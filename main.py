import os
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import ALLOWED_ORIGINS
from db import ensure_indexes, hotspots_collection, requests_collection
from models import (
    Hotspot,
    HotspotsResponse,
    IncomingRequest,
    IncomingRequestAccepted,
    RequestStatus,
)
from pipeline.graph import run_pipeline
from scoring.run_scoring import recompute_hotspots

app = FastAPI(title="JanSetu API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the static dir exists — git doesn't track empty folders, so this
# won't exist on a fresh deploy until ElevenLabs TTS writes the first file.
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup():
    ensure_indexes()


# ---- POST /api/requests -----------------------------------------------

@app.post("/api/requests", response_model=IncomingRequestAccepted, status_code=202)
def create_request(payload: IncomingRequest, background_tasks: BackgroundTasks):
    try:
        payload.validate_payload()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc = {
        "source": payload.source,
        "input_type": payload.input_type,
        "status": "processing",
        "created_at": datetime.now(timezone.utc),
    }
    inserted = requests_collection().insert_one(doc)
    request_id = str(inserted.inserted_id)

    background_tasks.add_task(
        _run_pipeline_and_persist,
        request_id,
        payload,
    )

    return IncomingRequestAccepted(request_id=request_id)


def _run_pipeline_and_persist(request_id: str, payload: IncomingRequest):
    state = {
        "request_id": request_id,
        "input_type": payload.input_type,
        "audio_base64": payload.audio_base64,
        "text": payload.text,
        "language_hint": payload.language_hint,
        "reported_lat": payload.reported_location.lat if payload.reported_location else None,
        "reported_lng": payload.reported_location.lng if payload.reported_location else None,
        "reported_place_name": payload.reported_location.place_name if payload.reported_location else None,
    }

    try:
        result = run_pipeline(state)
        requests_collection().update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {
                "status": "done",
                "raw_text": payload.text,
                "translated_text": result.get("english_text"),
                "language_detected": result.get("language_detected"),
                "category": result.get("category"),
                "lat": result.get("lat"),
                "lng": result.get("lng"),
                "district": result.get("district"),
                "confirmation_audio_url": result.get("confirmation_audio_url"),
            }},
        )
    except Exception as e:
        requests_collection().update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "failed", "error": str(e)}},
        )


# ---- GET /api/requests/{id} --------------------------------------------

@app.get("/api/requests/{request_id}", response_model=RequestStatus)
def get_request_status(request_id: str):
    try:
        doc = requests_collection().find_one({"_id": ObjectId(request_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="invalid request_id")

    if not doc:
        raise HTTPException(status_code=404, detail="request not found")

    return RequestStatus(
        request_id=str(doc["_id"]),
        status=doc["status"],
        category=doc.get("category"),
        translated_text=doc.get("translated_text"),
        language_detected=doc.get("language_detected"),
        district=doc.get("district"),
        confirmation_audio_url=doc.get("confirmation_audio_url"),
        error=doc.get("error"),
    )


# ---- GET /api/requests (raw feed, optional) -----------------------------

@app.get("/api/requests")
def list_requests(limit: int = 100):
    docs = requests_collection().find().sort("created_at", -1).limit(limit)
    return {
        "requests": [
            {
                "request_id": str(d["_id"]),
                "category": d.get("category"),
                "district": d.get("district"),
                "source": d.get("source"),
                "created_at": d["created_at"].isoformat() if d.get("created_at") else None,
            }
            for d in docs
        ]
    }


# ---- GET /api/hotspots ---------------------------------------------------

@app.get("/api/hotspots", response_model=HotspotsResponse)
def get_hotspots(category: str | None = None, district: str | None = None):
    query = {}
    if category:
        query["category"] = category
    if district:
        query["district"] = district

    docs = list(hotspots_collection().find(query).sort("rank", 1))
    if not docs:
        return HotspotsResponse(hotspots=[], generated_at=None)

    hotspots = [
        Hotspot(
            cluster_id=d["cluster_id"],
            category=d["category"],
            district=d["district"],
            center_lat=d["center_lat"],
            center_lng=d["center_lng"],
            request_count=d["request_count"],
            priority_score=d["priority_score"],
            explainability_text=d["explainability_text"],
            rank=d["rank"],
        )
        for d in docs
    ]
    return HotspotsResponse(hotspots=hotspots, generated_at=docs[0].get("generated_at"))


# ---- POST /api/hotspots/recompute (convenience for demo) ----------------

@app.post("/api/hotspots/recompute")
def trigger_recompute():
    count = recompute_hotspots()
    return {"hotspots_computed": count}