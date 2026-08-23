"""
Turns a raw cluster (from clustering.py) into a scored, explainable hotspot.

priority_score = w1 * volume_component
               + w2 * category_severity
               + w3 * deprivation_index
               + w4 * scheme_alignment_bonus

Scaled to 0-100. Weights are a starting point tuned for a demo dataset of
~40-60 requests — if your seed data is a different scale, adjust
VOLUME_NORMALIZATION accordingly so scores don't all cluster near 0 or 100.
"""
import json
import os

from pipeline.classify import CATEGORY_SEVERITY_WEIGHT

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

with open(os.path.join(_DATA_DIR, "deprivation_index.json")) as f:
    DEPRIVATION_INDEX = json.load(f)

with open(os.path.join(_DATA_DIR, "scheme_alignment.json")) as f:
    SCHEME_ALIGNMENT = json.load(f)

WEIGHTS = {
    "volume": 0.35,
    "severity": 0.20,
    "deprivation": 0.30,
    "scheme_bonus": 0.15,
}

# Requests-in-cluster count that maps to a "maxed out" volume component.
# A cluster with this many requests or more scores 1.0 on the volume axis.
VOLUME_NORMALIZATION = 40


def score_cluster(cluster: dict) -> dict:
    volume_component = min(cluster["request_count"] / VOLUME_NORMALIZATION, 1.0)
    severity_component = CATEGORY_SEVERITY_WEIGHT.get(cluster["category"], 0.5)
    deprivation_component = DEPRIVATION_INDEX.get(cluster["district"], DEPRIVATION_INDEX["unknown"])
    scheme = SCHEME_ALIGNMENT.get(cluster["category"])
    scheme_bonus_component = 1.0 if scheme else 0.0

    raw_score = (
        WEIGHTS["volume"] * volume_component
        + WEIGHTS["severity"] * severity_component
        + WEIGHTS["deprivation"] * deprivation_component
        + WEIGHTS["scheme_bonus"] * scheme_bonus_component
    )
    priority_score = round(raw_score * 100, 1)

    explainability_text = _build_explanation(cluster, deprivation_component, scheme)

    return {
        **cluster,
        "priority_score": priority_score,
        "explainability_text": explainability_text,
    }


def _build_explanation(cluster: dict, deprivation_component: float, scheme: str | None) -> str:
    parts = [f"{cluster['request_count']} requests clustered in {cluster['district']}"]

    if deprivation_component >= 0.65:
        parts.append(f"{cluster['category']} infrastructure index in the bottom quartile")
    elif deprivation_component <= 0.35:
        parts.append(f"{cluster['category']} infrastructure index relatively better-served")
    else:
        parts.append(f"{cluster['category']} infrastructure index around median")

    if scheme:
        parts.append(f"aligns with {scheme} gap")

    return ", ".join(parts) + "."


def rank_clusters(scored_clusters: list[dict]) -> list[dict]:
    ranked = sorted(scored_clusters, key=lambda c: c["priority_score"], reverse=True)
    for i, cluster in enumerate(ranked, start=1):
        cluster["rank"] = i
    return ranked
