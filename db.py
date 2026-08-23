from pymongo import MongoClient
from pymongo.collection import Collection

from config import MONGODB_URI, DB_NAME

_client = MongoClient(MONGODB_URI)
_db = _client[DB_NAME]


def get_db():
    return _db


def requests_collection() -> Collection:
    return _db["requests"]


def hotspots_collection() -> Collection:
    return _db["hotspots"]


def ensure_indexes():
    """Call once at startup. Cheap no-op if indexes already exist."""
    requests_collection().create_index("status")
    requests_collection().create_index([("lat", 1), ("lng", 1)])
    hotspots_collection().create_index("rank")
    hotspots_collection().create_index("category")
    hotspots_collection().create_index("district")
