"""
Clusters citizen requests into geographic "demand hotspots" using DBSCAN with
a haversine distance metric (so eps is expressed in real-world kilometers,
not raw lat/lng degrees).

Clustering runs separately per category — a water cluster and a road cluster
in the same physical area are different hotspots, and mixing them would blur
the priority-score story (see priority_score.py) that judges will ask about.
"""
import numpy as np
from sklearn.cluster import DBSCAN

EARTH_RADIUS_KM = 6371.0

# Requests within this radius of each other, in the same category, count as
# the same hotspot. Tune based on how spread your seed data is — start wide
# for a city-scale demo, narrow it if everything collapses into one cluster.
EPS_KM = 2.0
MIN_SAMPLES = 3


def cluster_requests(requests: list[dict]) -> list[dict]:
    """
    requests: list of dicts with at least 'lat', 'lng', 'category', 'district'
              (already filtered to exclude lat/lng == None upstream)

    Returns: list of cluster dicts:
      {cluster_id, category, district, center_lat, center_lng,
       request_count, member_ids}
    """
    clusters = []
    by_category: dict[str, list[dict]] = {}
    for r in requests:
        by_category.setdefault(r["category"], []).append(r)

    cluster_counter = 0
    for category, reqs in by_category.items():
        if len(reqs) < MIN_SAMPLES:
            continue

        coords = np.radians(np.array([[r["lat"], r["lng"]] for r in reqs]))
        eps_radians = EPS_KM / EARTH_RADIUS_KM

        db = DBSCAN(eps=eps_radians, min_samples=MIN_SAMPLES, metric="haversine")
        labels = db.fit_predict(coords)

        for label in set(labels):
            if label == -1:
                continue  # noise point, not part of any hotspot
            members = [reqs[i] for i in range(len(reqs)) if labels[i] == label]
            lats = [m["lat"] for m in members]
            lngs = [m["lng"] for m in members]
            districts = [m["district"] for m in members]
            dominant_district = max(set(districts), key=districts.count)

            cluster_counter += 1
            clusters.append({
                "cluster_id": f"cluster_{cluster_counter:03d}",
                "category": category,
                "district": dominant_district,
                "center_lat": float(np.mean(lats)),
                "center_lng": float(np.mean(lngs)),
                "request_count": len(members),
                "member_ids": [m["_id"] for m in members],
            })

    return clusters
