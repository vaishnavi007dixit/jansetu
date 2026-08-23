"""
Classifies a citizen report into an infrastructure category.

Keyword-based on purpose: it's deterministic, needs no API key, and is good
enough for a hackathon demo dataset. If you have time left and an LLM API key
available, swap classify() to a single LangChain/LangGraph LLM call with a
structured-output prompt — the function signature stays the same, so nothing
downstream needs to change.
"""

CATEGORY_KEYWORDS = {
    "water": ["water", "supply", "tap", "pipeline", "drainage", "sewage", "borewell", "tanker"],
    "road": ["road", "pothole", "street", "footpath", "highway", "traffic", "bridge"],
    "electricity": ["electricity", "power cut", "power", "transformer", "voltage", "streetlight", "outage"],
    "sanitation": ["garbage", "waste", "trash", "sanitation", "toilet", "cleanliness", "dump"],
    "health": ["hospital", "clinic", "phc", "doctor", "medicine", "health center", "ambulance"],
    "education": ["school", "teacher", "classroom", "education", "college", "anganwadi"],
}

CATEGORY_SEVERITY_WEIGHT = {
    "water": 1.0,
    "health": 1.0,
    "electricity": 0.85,
    "sanitation": 0.75,
    "road": 0.7,
    "education": 0.65,
    "other": 0.5,
}


def classify(english_text: str) -> str:
    text = english_text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits:
            scores[category] = hits
    if not scores:
        return "other"
    return max(scores, key=scores.get)
