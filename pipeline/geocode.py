"""
Resolves a district name from either:
  (a) lat/lng the frontend already sent (reverse geocode), or
  (b) a place_name string the frontend sent, or
  (c) neither — returns "unknown" district, request still gets stored but
      is excluded from clustering (see scoring/clustering.py).

Uses Nominatim (OpenStreetMap) — free, no API key, rate-limited to ~1 req/sec.
That's fine for a hackathon demo volume; do not use this in production without
a paid geocoding provider or your own tile server.
"""
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

_geolocator = Nominatim(user_agent="jansetu-hackathon")


def resolve_location(lat: float | None, lng: float | None, place_name: str | None) -> dict:
    """
    Returns: {"lat": float|None, "lng": float|None, "district": str}
    """
    if lat is not None and lng is not None:
        try:
            location = _geolocator.reverse((lat, lng), language="en", timeout=5, addressdetails=True)
            district = _extract_district(location.raw.get("address", {})) if location else "unknown"
            return {"lat": lat, "lng": lng, "district": district}
        except GeopyError:
            return {"lat": lat, "lng": lng, "district": "unknown"}

    if place_name:
        try:
            location = _geolocator.geocode(place_name, language="en", timeout=5, country_codes="in", addressdetails=True)
            if location:
                district = _extract_district(location.raw.get("address", {})) if hasattr(location, "raw") else "unknown"
                return {"lat": location.latitude, "lng": location.longitude, "district": district}
        except GeopyError:
            pass

    return {"lat": None, "lng": None, "district": "unknown"}


def _extract_district(address: dict) -> str:
    for key in ("state_district", "county", "district", "city", "town", "suburb"):
        if key in address:
            return address[key]
    return "unknown"
