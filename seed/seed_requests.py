"""
Seeds ~48 synthetic-but-plausible citizen requests across 3 categories and
3 Delhi-area districts, already in "done" status with lat/lng/district
filled in — so scoring/run_scoring.py has something real to cluster without
needing to record 48 real voice reports tonight.

Run: python -m seed.seed_requests
Then: python -m scoring.run_scoring
"""
import random
from datetime import datetime, timedelta, timezone

from db import requests_collection

random.seed(42)

# (district, category, center_lat, center_lng, sample_texts)
CLUSTERS = [
    ("North West Delhi", "water", 28.7041, 77.1025, [
        "There has been no water supply in our area for five days",
        "The water tanker has not come this week",
        "Water pipeline burst near the market, wasting supply",
    ]),
    ("North West Delhi", "water", 28.7010, 77.1080, [
        "Drinking water is contaminated in our locality",
        "No water pressure in the tap for days",
    ]),
    ("South Delhi", "road", 28.5245, 77.1855, [
        "Huge pothole on the main road causing accidents",
        "Street has not been repaired in months",
        "Footpath is broken and unsafe for pedestrians",
    ]),
    ("East Delhi", "electricity", 28.6280, 77.2900, [
        "Frequent power cuts every evening",
        "Transformer near our street is sparking",
        "Streetlights have not worked in weeks",
    ]),
    ("North East Delhi", "water", 28.6700, 77.2900, [
        "No piped water connection in this colony",
        "Water quality is very poor, causing illness",
    ]),
    ("North East Delhi", "sanitation", 28.6730, 77.2950, [
        "Garbage has not been collected in two weeks",
        "Open drain near the school is a health hazard",
    ]),
]

TOTAL_TARGET = 48


def build_docs():
    docs = []
    now = datetime.now(timezone.utc)
    per_cluster = TOTAL_TARGET // len(CLUSTERS)

    for district, category, base_lat, base_lng, texts in CLUSTERS:
        for i in range(per_cluster):
            jitter_lat = base_lat + random.uniform(-0.01, 0.01)
            jitter_lng = base_lng + random.uniform(-0.01, 0.01)
            text = random.choice(texts)
            docs.append({
                "source": random.choice(["voice", "text", "chat"]),
                "input_type": "text",
                "status": "done",
                "raw_text": text,
                "translated_text": text,
                "language_detected": random.choice(["hi", "en"]),
                "category": category,
                "lat": jitter_lat,
                "lng": jitter_lng,
                "district": district,
                "confirmation_audio_url": None,
                "created_at": now - timedelta(hours=random.randint(0, 96)),
            })
    return docs


def seed():
    docs = build_docs()
    requests_collection().insert_many(docs)
    print(f"Inserted {len(docs)} seed requests.")


if __name__ == "__main__":
    seed()
