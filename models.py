from typing import Literal, Optional

from pydantic import BaseModel, Field


class ReportedLocation(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    place_name: Optional[str] = None


class IncomingRequest(BaseModel):
    source: Literal["voice", "text", "chat"]
    input_type: Literal["audio", "text"]
    audio_base64: Optional[str] = None
    text: Optional[str] = None
    language_hint: Optional[str] = None
    reported_location: Optional[ReportedLocation] = None

    def validate_payload(self):
        if self.input_type == "audio" and not self.audio_base64:
            raise ValueError("audio_base64 is required when input_type is audio")
        if self.input_type == "text" and not self.text:
            raise ValueError("text is required when input_type is text")


class IncomingRequestAccepted(BaseModel):
    request_id: str
    status: Literal["processing"] = "processing"


class RequestStatus(BaseModel):
    request_id: str
    status: Literal["processing", "done", "failed"]
    category: Optional[str] = None
    translated_text: Optional[str] = None
    language_detected: Optional[str] = None
    district: Optional[str] = None
    confirmation_audio_url: Optional[str] = None
    error: Optional[str] = None


class Hotspot(BaseModel):
    cluster_id: str
    category: str
    district: str
    center_lat: float
    center_lng: float
    request_count: int
    priority_score: float
    explainability_text: str
    rank: int


class HotspotsResponse(BaseModel):
    hotspots: list[Hotspot]
    generated_at: Optional[str] = None
