"""
Recomputes hotspots from scratch. Run standalone:

    python -m scoring.run_scoring

Or triggered on-demand via POST /api/hotspots/recompute (see main.py) —
useful for the demo: submit a few live reports, hit recompute, watch the
dashboard's ranking change.
"""
from datetime import datetime, timezone

from db import requests_collection, hotspots_collection
from scoring.clustering import cluster_requests
from scoring.priority_score import score_cluster, rank_clusters


def recompute_hotspots() -> int:
    docs = list(requests_collection().find({
        "status": "done",
        "lat": {"$ne": None},
        "lng": {"$ne": None},
    }))

    if not docs:
        hotspots_collection().delete_many({})
        return 0

    clusters = cluster_requests(docs)
    scored = [score_cluster(c) for c in clusters]
    ranked = rank_clusters(scored)

    for cluster in ranked:
        cluster.pop("member_ids", None)  # internal only, not part of the API contract shape
        cluster["generated_at"] = datetime.now(timezone.utc).isoformat()

    hotspots_collection().delete_many({})
    if ranked:
        hotspots_collection().insert_many(ranked)

    return len(ranked)


if __name__ == "__main__":
    count = recompute_hotspots()
    print(f"Recomputed {count} hotspots.")
